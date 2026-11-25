from sqlalchemy import Column, Integer, String, Float

try:
    from app.db.database import Base
except ImportError:
    from db.database import Base


class CityCommunity(Base):
    """
    Chicago City Community Areas lookup model.
    Contains demographic, area, and density metrics for all 77 official community areas.
    """
    __tablename__ = "city_community"
    __table_args__ = {'extend_existing': True}

    community_code   = Column(Integer, primary_key=True, index=True)
    community_name   = Column(String(100), nullable=False, index=True)
    population       = Column(String(50), nullable=True)
    area_sqmile      = Column(Float, nullable=True)
    area_sqkm        = Column(Float, nullable=True)
    density_per_sqmi = Column(String(50), nullable=True)
    density_per_sqkm = Column(String(50), nullable=True)
