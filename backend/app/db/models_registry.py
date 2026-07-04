"""
Importing this module guarantees every domain's models are registered on
Base.metadata - required before create_all()/Alembic autogenerate can see
the full schema, and before SQLAlchemy resolves the string-based
relationship() targets used across domain boundaries.

Add new domains' model modules here as they're created.
"""

from app.domains.appointments import models as _appointments_models  # noqa: F401
from app.domains.calls import models as _calls_models  # noqa: F401
from app.domains.caregivers import models as _caregivers_models  # noqa: F401
from app.domains.medications import models as _medications_models  # noqa: F401
from app.domains.patients import models as _patients_models  # noqa: F401
from app.domains.timeline import models as _timeline_models  # noqa: F401
