from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float

class ChicagoCrime(Base):
    __tablename__ = "chicago_crime"
    __table_args__ = {'extend_existing': True}
    
    # Primary Key & Identification
    id             = Column(Integer, primary_key=True)
    case_number    = Column(String(20))
    date           = Column(DateTime)
    date_of_update = Column(DateTime)
    block          = Column(String(100))
    iucr_code      = Column(String(10))
    location_desc  = Column(String(50))
    
    # Incident Characteristics
    arrest         = Column(Boolean)
    domestic       = Column(Boolean)
    
    # Geographic Hierarchy
    beat_num       = Column(Integer)
    district_code  = Column(Integer)
    ward_no        = Column(Integer)
    community_code = Column(Integer)
    fbi_code       = Column(String(10))
    
    # Spatial Coordinates (nullable to maintain genuine missingness)
    x_coordinate   = Column(Float, nullable=True)
    y_coordinate   = Column(Float, nullable=True)
    latitude       = Column(Float, nullable=True)
    longitude      = Column(Float, nullable=True)
    location       = Column(String(100), nullable=True)
    
    # Engineered Date Features
    Year           = Column(Integer)
    Month          = Column(Integer)
    DayOfWeek      = Column(String(20))