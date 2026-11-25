from sqlalchemy import Column, Integer, String, Float

try:
    from app.db.database import Base
except ImportError:
    from db.database import Base


class DistrictPSInfo(Base):
    """
    Chicago Police Department District Police Stations model.
    Contains station addresses, contact info, and spatial coordinates.
    """
    __tablename__ = "district_ps_info"
    __table_args__ = {'extend_existing': True}

    district_code = Column(Integer, primary_key=True, index=True)
    district_name = Column(String(100), nullable=False)
    address       = Column(String(150), nullable=True)
    city          = Column(String(50), nullable=True)
    state         = Column(String(10), nullable=True)
    zip           = Column(Integer, nullable=True)
    website       = Column(String(255), nullable=True)
    phone         = Column(String(50), nullable=True)
    fax           = Column(String(50), nullable=True)
    tty           = Column(String(50), nullable=True)
    x_coordinate  = Column(Float, nullable=True)
    y_coordinate  = Column(Float, nullable=True)
    latitude      = Column(Float, nullable=True)
    longitude     = Column(Float, nullable=True)
    location      = Column(String(100), nullable=True)
