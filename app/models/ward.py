from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

try:
    from app.db.database import Base
except ImportError:
    from db.database import Base


class WardOffice(Base):
    """
    Chicago Ward Offices model.
    Contains City Council alderman info, municipal ward offices, and contacts.
    """
    __tablename__ = "ward_office"
    __table_args__ = {'extend_existing': True}

    ward              = Column(Integer, primary_key=True, index=True)
    alderman          = Column(String(100), nullable=False)
    address           = Column(String(150), nullable=True)
    city              = Column(String(50), nullable=True)
    state             = Column(String(10), nullable=True)
    zipcode           = Column(Integer, nullable=True)
    ward_phone        = Column(String(50), nullable=True)
    ward_fax          = Column(String(50), nullable=True)
    email             = Column(String(100), nullable=True)
    website           = Column(String(255), nullable=True)
    longitude         = Column(Float, nullable=True)
    latitude          = Column(Float, nullable=True)
    city_hall_address = Column(String(150), nullable=True)
    city_hall_city    = Column(String(50), nullable=True)
    city_hall_state   = Column(String(10), nullable=True)
    city_hall_zipcode = Column(Integer, nullable=True)
    city_hall_phone   = Column(String(50), nullable=True)

    crimes = relationship("ChicagoCrime", back_populates="ward_office")
