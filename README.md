# HealthBuddy AI — Medication Reminder Call Platform (Telnyx)

Two call flows, both via Telnyx Call Control, backing the two screens this was built from:

- **System → patient (scheduled)**: a background scheduler dials the patient automatically
  at each medication's scheduled time, runs a scripted yes/no IVR check, and logs the
  outcome. This is the **AI Call Center** screen.
- **Caregiver → patient (on demand)**: a caregiver clicks "Start call," and the backend
  dials the caregiver first, then bridges in the patient once the caregiver picks up —
  a real two-way conversation, not a script. This is the **Call patient** screen.

There is no "call anyone, anytime" AI-calling endpoint by design — system calls only ever
fire from the scheduler against a due, unresolved dose.

```
med-reminder-telnyx/
  backend/     FastAPI, domain-oriented modules, Alembic migrations, APScheduler
  frontend/    Next.js (App Router, TypeScript, Tailwind) — talks to backend only over HTTP
  docker-compose.yml
```

The frontend and backend are fully separate deployables; the frontend only ever calls the
backend's HTTP API (`NEXT_PUBLIC_API_URL`).

## Backend architecture — why it's organized this way

The backend is split into self-contained **domains** under `backend/app/domains/`, each
owning its own models, schemas, and router. This is the thing to extend as the product
grows — a new feature almost always means a new domain folder, not edits scattered across
a `routers.py`/`models.py` pair.

```
backend/app/
  core/                    config, shared enums, auth guard - no domain logic
  db/                      SQLAlchemy base, session factory, models_registry
  domains/
    patients/              Patient + health snapshot composition
    caregivers/             Caregiver + "current caregiver" stub (see auth note below)
    medications/              Medication, MedicationSchedule, Dose + dose generation
    appointments/               Appointment
    calls/                        Call, CallEvent, Telnyx client, IVR + bridging orchestration
    timeline/                      TimelineEvent - the health-timeline audit log
    dashboard/                       Cross-domain aggregation (adherence, response breakdown)
  scheduler/               APScheduler jobs: generate today's doses, dispatch due calls
  main.py                  Wires every domain router + the scheduler lifecycle
  seed.py                  Idempotent demo data (Robert Mitchell / Sarah Mitchell)
```

**Cross-domain references** (e.g. `Call.patient_id`, `Dose.calls`) resolve through
SQLAlchemy's shared registry via string-based `relationship()` targets and
`TYPE_CHECKING`-only imports — domain modules never import each other's models directly at
runtime, so there's no risk of circular imports as more domains get added. `db/models_registry.py`
is the one place that imports every domain's models; anything that queries the database
before that (a script, a worker, a test) needs to import it first — `main.py`, `seed.py`,
`alembic/env.py`, and `scheduler/jobs.py` all already do this.

**Adding a new domain** (e.g. "labs"): create `domains/labs/{models,schemas,router}.py`,
add `labs` to `db/models_registry.py`, include its router in `main.py`, and generate a
migration (`alembic revision --autogenerate`). Nothing else needs to change.

## The two call flows in detail

### System → patient (`app/domains/calls/service.py::trigger_system_call` + `_handle_system_event`)

A single Telnyx call leg. On answer, the backend calls `gather_using_speak` (speaks the
reminder, collects a DTMF `1`/`2`) and `transcription_start` (captures spoken "yes"/"no")
in parallel — whichever resolves first wins, the other is stopped. The result updates the
`Dose` status:

| Outcome | Dose status |
|---|---|
| "Yes" (digit `1` or speech) | `confirmed` |
| "No" (digit `2` or speech) | `missed` |
| Unclear answer, or never answered at all | `escalated` |

Every webhook event is written to `CallEvent` and a summary is written to `TimelineEvent`.

### Caregiver → patient (`trigger_caregiver_call` + `_handle_caregiver_leg_event` / `_handle_patient_leg_event`)

Two Telnyx call legs, correlated by a shared `Call.id` encoded into each leg's
`client_state` (with a `leg` tag — `"caregiver"` or `"patient"` — so events from either leg
route to the right handler):

1. Dial the caregiver (`call_control_id`).
2. On the caregiver answering, speak "Connecting you now" and dial the patient
   (`patient_call_control_id`).
3. On the patient answering, `bridge()` the two legs — from here it's a normal live call.
4. Whichever leg hangs up first ends the other; exactly one "Caregiver call ended" timeline
   entry is written regardless of which leg's hangup webhook arrives first (see the
   `already_completed` guard in `service.py` — this was a real double-write bug caught
   during testing and is worth understanding if you touch this code).

Video calls are accepted by the API shape (`call_type: "video"`) but rejected with a clear
422 — see `VideoNotSupportedError` — since that requires a companion app this backend
doesn't provide.

## The scheduler (`app/scheduler/`)

Two jobs, run in-process via APScheduler:

- **`ensure_todays_doses_job`** (daily at 00:00 UTC, plus once at startup): materializes a
  `Dose` row for today from each active `MedicationSchedule`. Idempotent via a DB unique
  constraint on `(medication_schedule_id, scheduled_for)`.
- **`dispatch_due_calls_job`** (every `DOSE_DISPATCH_INTERVAL_SECONDS`, default 30s): finds
  doses that are due and have no `Call` row yet, and places the system call for each.

**Why "has no Call row yet" and not "status is still pending"**: a dose stays `pending`
for the entire time its call is ringing/in-progress — only resolution changes the status.
Checking status alone would re-dial the same dose on every tick until it resolves. This
was a real bug caught during testing; the fix is the `~exists()` subquery in
`jobs.py::dispatch_due_calls_job`.

**Scaling beyond one backend instance**: this in-process scheduler is correct for a single
replica. Running multiple replicas would run multiple copies of it and could double-dispatch
before the first `Call` row commits. Fix by either moving dispatch to one dedicated worker
process, or wrapping the job in a Postgres advisory lock keyed on a fixed name — `jobs.py`
itself doesn't need to change either way.

## Setup

### 1. Telnyx (one-time, manual)

1. Sign up at [telnyx.com](https://telnyx.com), open the
   [Mission Control Portal](https://portal.telnyx.com).
2. **Numbers → Buy Numbers**: provision one voice-capable number.
3. **Call Control → Applications**: create a Call Control Application, note its
   **Connection ID**.
4. **Account Settings → API Keys**: copy your API key.
5. **Account Settings → Public Key**: copy the Ed25519 public key (webhook signature
   verification).

### 2. Run with Docker (Postgres + backend)

```bash
cp backend/.env.example backend/.env
# fill in TELNYX_API_KEY, TELNYX_CONNECTION_ID, TELNYX_PUBLIC_KEY, TELNYX_PHONE_NUMBER

docker compose up --build
```

`entrypoint.sh` runs `alembic upgrade head` automatically, then (if `SEED_DEMO_DATA=true`,
the default) `python -m app.seed`. Check it's alive: `curl http://localhost:8000/health`.

Using **Supabase** instead of the bundled Postgres? Set `DATABASE_URL` in `backend/.env` to
your Supabase connection string and run `docker compose up backend` — see the comment in
`docker-compose.yml` for the one line to remove.

### 3. Run locally without Docker (for backend development)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local or Supabase Postgres

alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### 4. Expose the backend to Telnyx with ngrok

Works identically whether the backend is containerized or run directly, since either way
it's just listening on `localhost:8000`:

```bash
ngrok http 8000
```

Copy the `https://xxxx.ngrok-free.app` URL into `PUBLIC_BASE_URL` in `backend/.env`, then
`docker compose restart backend` (or restart `uvicorn` if running locally).

### 5. Run the frontend

```bash
cd frontend
cp .env.local.example .env.local     # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

Open **http://localhost:3000** — the "Call patient" screen. **http://localhost:3000/ai-call-center**
is the AI Call Center screen. Both poll the backend every few seconds.

Containerized instead: `docker compose --profile frontend up --build`.

### 6. Try it

- **Caregiver call**: pick a call reason, optionally add a private note, hit "Start call."
  The backend dials the caregiver's seeded number first (Telnyx trial accounts can only
  reach verified numbers — verify your own test number in the Telnyx portal first).
- **AI call**: either wait for a dose's scheduled time, or hit "Call now" next to a pending
  dose in the AI Call Center's "Today's schedule" panel to trigger it immediately
  (`POST /calls/system`).

## Database — local & deployment

Schema is entirely owned by Alembic migrations (`backend/alembic/versions/`) — nothing
auto-creates tables at runtime. This is deliberately testable both ways:

```bash
# Local: point at anything Postgres-compatible
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/med_reminder alembic upgrade head

# Deployment: point at Supabase, RDS, etc. - same command, same migrations
DATABASE_URL=postgresql://postgres:PASSWORD@your-project.supabase.co:5432/postgres alembic upgrade head
```

Create a new migration after changing any `models.py`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Every migration in this repo was generated and applied against a real local Postgres
instance (including a full `upgrade` → `downgrade base` → `upgrade` round-trip) before being
committed — not hand-written blind.

## Security notes

- `VALIDATE_TELNYX_SIGNATURE=true` verifies Telnyx's Ed25519 webhook signature over the raw
  request body before any event is processed.
- The webhook never trusts a `call_control_id` alone — every event is matched to a `Call`
  row via `client_state`; unmatched events are acknowledged and ignored.
- Set `DEMO_ADMIN_TOKEN` in `backend/.env` to require a bearer token on every API route
  (not the webhook) — set the matching `NEXT_PUBLIC_API_TOKEN` in `frontend/.env.local` so
  the console keeps working.
- CORS (`ALLOWED_ORIGINS`) defaults to the Next.js dev origin — lock this down in production.

## What's intentionally out of scope (and the plan for it)

- **Real caregiver authentication.** `GET /caregivers/me` currently returns "the first
  seeded caregiver" — every call site that needs "the current caregiver" already goes
  through that one function on the backend, and `usePrimaryContext()` is the equivalent
  single choke point on the frontend. Swapping in real sessions (JWT, OAuth) means changing
  those two functions, not hunting through the codebase.
- **Multi-caregiver-per-patient.** `Patient.primary_caregiver_id` is a single FK today. A
  real multi-caregiver model would add a `caregiver_patient_links` join table; the rest of
  the schema doesn't need to change.
- **Video calls.** Accepted by the API shape, rejected with a clear 422 — needs a WebRTC/
  companion-app integration this backend doesn't provide.
- **Horizontally-scaled scheduler.** See the scheduler section above.

## Production hardening checklist

- Run `alembic upgrade head` as a distinct deploy step once you have multiple backend
  replicas, rather than on every container boot.
- Put the backend behind gunicorn + multiple uvicorn workers (commented line in
  `backend/Dockerfile`).
- Move `PUBLIC_BASE_URL` to a stable domain instead of ngrok.
- Layer real authentication per the note above.
- Front the frontend with a CDN; set `NEXT_PUBLIC_API_URL` per environment at build time.
