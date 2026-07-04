"""
Seeds one demo caregiver/patient/medication set so the app is immediately
useful on a fresh database - matches the "Robert Mitchell" / "Sarah
Mitchell" example used throughout the frontend. Idempotent: safe to run
more than once.

Usage:
    python -m app.seed
"""

import asyncio
import datetime as dt
import logging

from sqlalchemy import select

from app.db import models_registry  # noqa: F401  (registers every domain's models before any query runs)
from app.db.session import AsyncSessionLocal
from app.domains.appointments.models import Appointment
from app.domains.caregivers.models import Caregiver
from app.domains.medications.models import Medication, MedicationSchedule
from app.domains.medications.service import ensure_doses_for_date
from app.domains.patients.models import Patient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.seed")

DEMO_CAREGIVER_EMAIL = "sarah@example.com"


async def seed_demo_data() -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(Caregiver).where(Caregiver.email == DEMO_CAREGIVER_EMAIL))
        if existing.scalar_one_or_none():
            logger.info("Demo data already present - skipping seed")
            return

        today = dt.date.today()

        caregiver = Caregiver(name="Sarah Mitchell", email=DEMO_CAREGIVER_EMAIL, phone_number="+15550001111")
        db.add(caregiver)
        await db.flush()

        patient = Patient(
            name="Robert Mitchell",
            date_of_birth=today.replace(year=today.year - 71),
            relation_to_caregiver="Your father",
            phone_number="+15550002222",
            phone_label="Primary · Mobile",
            ai_monitoring_enabled=True,
            primary_caregiver_id=caregiver.id,
            last_hba1c=7.2,
            last_hba1c_at=today - dt.timedelta(days=12),
        )
        db.add(patient)
        await db.flush()

        metformin = Medication(
            patient_id=patient.id, name="Metformin", dose_text="500mg", refill_due_on=today + dt.timedelta(days=3)
        )
        lisinopril = Medication(patient_id=patient.id, name="Lisinopril", dose_text="10mg")
        atorvastatin = Medication(patient_id=patient.id, name="Atorvastatin", dose_text="20mg")
        db.add_all([metformin, lisinopril, atorvastatin])
        await db.flush()

        db.add_all(
            [
                MedicationSchedule(
                    medication_id=metformin.id, patient_id=patient.id, time_of_day=dt.time(8, 0), label="Morning dose"
                ),
                MedicationSchedule(
                    medication_id=metformin.id, patient_id=patient.id, time_of_day=dt.time(21, 0), label="Evening dose"
                ),
                MedicationSchedule(
                    medication_id=lisinopril.id, patient_id=patient.id, time_of_day=dt.time(13, 0), label="Afternoon dose"
                ),
                MedicationSchedule(
                    medication_id=atorvastatin.id, patient_id=patient.id, time_of_day=dt.time(22, 0), label="Evening dose"
                ),
            ]
        )

        db.add(
            Appointment(
                patient_id=patient.id,
                doctor_name="Dr. Howard",
                scheduled_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=5),
            )
        )

        await db.commit()
        logger.info("Seeded demo caregiver %s and patient %s", caregiver.email, patient.name)

    async with AsyncSessionLocal() as db:
        created = await ensure_doses_for_date(db, target_date=today)
        logger.info("Generated %d dose(s) for today", created)


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
