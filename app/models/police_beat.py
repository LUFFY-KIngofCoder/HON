from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

try:
    from app.db.database import Base
except ImportError:
    from db.database import Base


class PoliceBeatInfo(Base):
    """
    Chicago Police Beat organizational hierarchy model.
    Maps beat numbers to their respective police sectors and districts.
    """
    __tablename__ = "police_beat_info"
    __table_args__ = {'extend_existing': True}

    beat_num = Column(Integer, primary_key=True, index=True)
    district = Column(Integer, nullable=False, index=True)
    sector   = Column(Integer, nullable=False)
    beat     = Column(Integer, nullable=False)

    crimes = relationship("ChicagoCrime", back_populates="beat")
