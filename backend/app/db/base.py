from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Single shared declarative base for every domain's models. Cross-domain
    relationships (e.g. Call -> Patient, Dose -> Call) resolve by class
    name through this shared registry, so domain model modules never need
    to import each other directly - see the TYPE_CHECKING-guarded imports
    in each domain's models.py.
    """

    pass
