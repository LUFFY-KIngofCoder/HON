from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

try:
    from app.db.database import Base
except ImportError:
    from db.database import Base


class IUCRCode(Base):
    """
    Illinois Uniform Crime Reporting (IUCR) lookup model.
    Maps 4-digit crime codes to Primary Types and secondary descriptions.
    """
    __tablename__ = "iucr_codes"
    __table_args__ = {'extend_existing': True}

    iucr         = Column(String(10), primary_key=True, index=True)
    primary_type = Column(String(100), nullable=False, index=True)
    description  = Column(String(255), nullable=False)
    index_code   = Column(String(10), nullable=True)

    crimes = relationship("ChicagoCrime", back_populates="iucr")
