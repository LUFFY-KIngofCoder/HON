from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class ChicagoCrime(Base):
    """
    Master incident model for Chicago Police Department crime records.
    Maps directly to the 'chicago_crime' table.
    """
    __tablename__ = "chicago_crime"
    __table_args__ = {'extend_existing': True}

    # Primary Key & Identification
    id             = Column(Integer, primary_key=True, index=True)
    case_number    = Column(String(50), nullable=False)
    date           = Column(DateTime, nullable=False, index=True)
    date_of_update = Column(DateTime, nullable=True)
    block          = Column(String(100), nullable=True)
    iucr_code      = Column(String(10), ForeignKey("iucr_codes.iucr"), nullable=False, index=True)
    location_desc  = Column(String(100), nullable=True)

    # Incident Characteristics
    arrest         = Column(Boolean, default=False, nullable=False, index=True)
    domestic       = Column(Boolean, default=False, nullable=False)

    # Law Enforcement & Geographic Hierarchy
    beat_num       = Column(Integer, ForeignKey("police_beat_info.beat_num"), nullable=True, index=True)
    district_code  = Column(Integer, ForeignKey("district_ps_info.district_code"), nullable=True, index=True)
    ward_no        = Column(Integer, ForeignKey("ward_office.ward"), nullable=True, index=True)
    community_code = Column(Integer, ForeignKey("city_community.community_code"), nullable=True, index=True)
    fbi_code       = Column(String(10), nullable=True)

    # Spatial Coordinates (nullable to maintain genuine missingness integrity)
    x_coordinate   = Column(Float, nullable=True)
    y_coordinate   = Column(Float, nullable=True)
    latitude       = Column(Float, nullable=True)
    longitude      = Column(Float, nullable=True)
    location       = Column(String(100), nullable=True)

    # Engineered Date Features
    Year           = Column(Integer, nullable=False, index=True)
    Month          = Column(Integer, nullable=False, index=True)
    DayOfWeek      = Column(String(20), nullable=False)
    Day            = Column(Integer, nullable=True)

    # ORM Relationships
    iucr        = relationship("IUCRCode", back_populates="crimes")
    beat        = relationship("PoliceBeatInfo", back_populates="crimes")
    district    = relationship("DistrictPSInfo", back_populates="crimes")
    ward_office = relationship("WardOffice", back_populates="crimes")
    community   = relationship("CityCommunity", back_populates="crimes")
