from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ── ChicagoCrime ──────────────────────────────────────────────────────────────

class ChicagoCrimeCreate(BaseModel):
    case_number:    str
    date:           Optional[datetime] = None
    date_of_update: Optional[datetime] = None
    block:          Optional[str]      = None
    iucr_code:      str
    location_desc:  Optional[str]      = None
    arrest:         bool               = False
    domestic:       bool               = False
    beat_num:       Optional[int]      = None
    district_code:  Optional[int]      = None
    ward_no:        Optional[int]      = None
    community_code: Optional[int]      = None
    fbi_code:       Optional[str]      = None
    x_coordinate:   Optional[float]    = None
    y_coordinate:   Optional[float]    = None
    latitude:       Optional[float]    = None
    longitude:      Optional[float]    = None
    location:       Optional[str]      = None
    Year:           int
    Month:          int
    DayOfWeek:      str
    Day:            Optional[int]      = None


class ChicagoCrimeUpdate(BaseModel):
    case_number:    Optional[str]      = None
    date:           Optional[datetime] = None
    date_of_update: Optional[datetime] = None
    block:          Optional[str]      = None
    iucr_code:      Optional[str]      = None
    location_desc:  Optional[str]      = None
    arrest:         Optional[bool]     = None
    domestic:       Optional[bool]     = None
    beat_num:       Optional[int]      = None
    district_code:  Optional[int]      = None
    ward_no:        Optional[int]      = None
    community_code: Optional[int]      = None
    fbi_code:       Optional[str]      = None
    x_coordinate:   Optional[float]    = None
    y_coordinate:   Optional[float]    = None
    latitude:       Optional[float]    = None
    longitude:      Optional[float]    = None
    location:       Optional[str]      = None
    Year:           Optional[int]      = None
    Month:          Optional[int]      = None
    DayOfWeek:      Optional[str]      = None
    Day:            Optional[int]      = None


class ChicagoCrimeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    case_number:    str
    date:           Optional[datetime] = None
    date_of_update: Optional[datetime] = None
    block:          Optional[str]      = None
    iucr_code:      str
    location_desc:  Optional[str]      = None
    arrest:         bool
    domestic:       bool
    beat_num:       Optional[int]   = None
    district_code:  Optional[int]   = None
    ward_no:        Optional[int]   = None
    community_code: Optional[int]   = None
    fbi_code:       Optional[str]   = None
    x_coordinate:   Optional[float] = None
    y_coordinate:   Optional[float] = None
    latitude:       Optional[float] = None
    longitude:      Optional[float] = None
    location:       Optional[str]   = None
    Year:           int
    Month:          int
    DayOfWeek:      str
    Day:            Optional[int]   = None


# ── IUCRCode ──────────────────────────────────────────────────────────────────

class IUCRCodeCreate(BaseModel):
    iucr:         str
    primary_type: str
    description:  str
    index_code:   Optional[str] = None


class IUCRCodeUpdate(BaseModel):
    primary_type: Optional[str] = None
    description:  Optional[str] = None
    index_code:   Optional[str] = None


class IUCRCodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iucr:         str
    primary_type: str
    description:  str
    index_code:   Optional[str] = None


# ── CityCommunity ─────────────────────────────────────────────────────────────

class CityCommunityCreate(BaseModel):
    community_code:   int
    community_name:   str
    population:       Optional[int]   = None
    area_sqmile:      Optional[float] = None
    area_sqkm:        Optional[float] = None
    density_per_sqmi: Optional[float] = None
    density_per_sqkm: Optional[float] = None


class CityCommunityUpdate(BaseModel):
    community_name:   Optional[str]   = None
    population:       Optional[int]   = None
    area_sqmile:      Optional[float] = None
    area_sqkm:        Optional[float] = None
    density_per_sqmi: Optional[float] = None
    density_per_sqkm: Optional[float] = None


class CityCommunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    community_code:   int
    community_name:   str
    population:       Optional[int]   = None
    area_sqmile:      Optional[float] = None
    area_sqkm:        Optional[float] = None
    density_per_sqmi: Optional[float] = None
    density_per_sqkm: Optional[float] = None


# ── DistrictPSInfo ────────────────────────────────────────────────────────────

class DistrictPSInfoCreate(BaseModel):
    district_code: int
    district_name: str
    address:       Optional[str]   = None
    city:          Optional[str]   = None
    state:         Optional[str]   = None
    zip:           Optional[int]   = None
    website:       Optional[str]   = None
    phone:         Optional[str]   = None
    fax:           Optional[str]   = None
    tty:           Optional[str]   = None
    x_coordinate:  Optional[float] = None
    y_coordinate:  Optional[float] = None
    latitude:      Optional[float] = None
    longitude:     Optional[float] = None
    location:      Optional[str]   = None


class DistrictPSInfoUpdate(BaseModel):
    district_name: Optional[str]   = None
    address:       Optional[str]   = None
    city:          Optional[str]   = None
    state:         Optional[str]   = None
    zip:           Optional[int]   = None
    website:       Optional[str]   = None
    phone:         Optional[str]   = None
    fax:           Optional[str]   = None
    tty:           Optional[str]   = None
    x_coordinate:  Optional[float] = None
    y_coordinate:  Optional[float] = None
    latitude:      Optional[float] = None
    longitude:     Optional[float] = None
    location:      Optional[str]   = None


class DistrictPSInfoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    district_code: int
    district_name: str
    address:       Optional[str]   = None
    city:          Optional[str]   = None
    state:         Optional[str]   = None
    zip:           Optional[int]   = None
    website:       Optional[str]   = None
    phone:         Optional[str]   = None
    fax:           Optional[str]   = None
    tty:           Optional[str]   = None
    x_coordinate:  Optional[float] = None
    y_coordinate:  Optional[float] = None
    latitude:      Optional[float] = None
    longitude:     Optional[float] = None
    location:      Optional[str]   = None


# ── PoliceBeatInfo ────────────────────────────────────────────────────────────

class PoliceBeatInfoCreate(BaseModel):
    beat_num: int
    district: int
    sector:   int
    beat:     int


class PoliceBeatInfoUpdate(BaseModel):
    district: Optional[int] = None
    sector:   Optional[int] = None
    beat:     Optional[int] = None


class PoliceBeatInfoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    beat_num: int
    district: int
    sector:   int
    beat:     int


# ── WardOffice ────────────────────────────────────────────────────────────────

class WardOfficeCreate(BaseModel):
    ward:              int
    alderman:          str
    address:           Optional[str]   = None
    city:              Optional[str]   = None
    state:             Optional[str]   = None
    zipcode:           Optional[int]   = None
    ward_phone:        Optional[str]   = None
    ward_fax:          Optional[str]   = None
    email:             Optional[str]   = None
    website:           Optional[str]   = None
    longitude:         Optional[float] = None
    latitude:          Optional[float] = None
    city_hall_address: Optional[str]   = None
    city_hall_city:    Optional[str]   = None
    city_hall_state:   Optional[str]   = None
    city_hall_zipcode: Optional[int]   = None
    city_hall_phone:   Optional[str]   = None


class WardOfficeUpdate(BaseModel):
    alderman:          Optional[str]   = None
    address:           Optional[str]   = None
    city:              Optional[str]   = None
    state:             Optional[str]   = None
    zipcode:           Optional[int]   = None
    ward_phone:        Optional[str]   = None
    ward_fax:          Optional[str]   = None
    email:             Optional[str]   = None
    website:           Optional[str]   = None
    longitude:         Optional[float] = None
    latitude:          Optional[float] = None
    city_hall_address: Optional[str]   = None
    city_hall_city:    Optional[str]   = None
    city_hall_state:   Optional[str]   = None
    city_hall_zipcode: Optional[int]   = None
    city_hall_phone:   Optional[str]   = None


class WardOfficeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ward:              int
    alderman:          str
    address:           Optional[str]   = None
    city:              Optional[str]   = None
    state:             Optional[str]   = None
    zipcode:           Optional[int]   = None
    ward_phone:        Optional[str]   = None
    ward_fax:          Optional[str]   = None
    email:             Optional[str]   = None
    website:           Optional[str]   = None
    longitude:         Optional[float] = None
    latitude:          Optional[float] = None
    city_hall_address: Optional[str]   = None
    city_hall_city:    Optional[str]   = None
    city_hall_state:   Optional[str]   = None
    city_hall_zipcode: Optional[int]   = None
    city_hall_phone:   Optional[str]   = None
