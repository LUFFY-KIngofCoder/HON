from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import inspect, String, or_, asc, desc, exc as sqlexc

from app.db.database import get_db
from app.models import (
    ChicagoCrime, IUCRCode, CityCommunity,
    DistrictPSInfo, PoliceBeatInfo, WardOffice,
)
from app.schemas.tables import (
    ChicagoCrimeCreate,    ChicagoCrimeUpdate,    ChicagoCrimeRead,
    IUCRCodeCreate,        IUCRCodeUpdate,        IUCRCodeRead,
    CityCommunityCreate,   CityCommunityUpdate,   CityCommunityRead,
    DistrictPSInfoCreate,  DistrictPSInfoUpdate,  DistrictPSInfoRead,
    PoliceBeatInfoCreate,  PoliceBeatInfoUpdate,  PoliceBeatInfoRead,
    WardOfficeCreate,      WardOfficeUpdate,      WardOfficeRead,
)

router = APIRouter(prefix="/api/tables", tags=["CRUD"])

# ── Registry: table_name → (Model, PK attr name, CreateSchema, UpdateSchema, ReadSchema)
_REGISTRY: dict[str, tuple] = {
    "chicago_crime":    (ChicagoCrime,   "id",            ChicagoCrimeCreate,   ChicagoCrimeUpdate,   ChicagoCrimeRead),
    "iucr_codes":       (IUCRCode,       "iucr",          IUCRCodeCreate,       IUCRCodeUpdate,       IUCRCodeRead),
    "city_community":   (CityCommunity,  "community_code",CityCommunityCreate,  CityCommunityUpdate,  CityCommunityRead),
    "district_ps_info": (DistrictPSInfo, "district_code", DistrictPSInfoCreate, DistrictPSInfoUpdate, DistrictPSInfoRead),
    "police_beat_info": (PoliceBeatInfo, "beat_num",      PoliceBeatInfoCreate, PoliceBeatInfoUpdate, PoliceBeatInfoRead),
    "ward_office":      (WardOffice,     "ward",          WardOfficeCreate,     WardOfficeUpdate,     WardOfficeRead),
}


def _resolve(table_name: str):
    entry = _REGISTRY.get(table_name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Unknown table: '{table_name}'. "
                            f"Valid tables: {list(_REGISTRY.keys())}")
    return entry


def _row_to_dict(row) -> dict:
    """Converts a SQLAlchemy model instance to a plain dict (excluding relationship attrs)."""
    return {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs}


def _get_string_cols(model) -> list:
    """Returns list of column attribute names whose type is String-based."""
    return [
        c.key for c in inspect(model).mapper.column_attrs
        if isinstance(inspect(model).mapper.columns[c.key].type, String)
    ]


# ── GET /api/tables/{table_name} — List with filter, search, sort, pagination ─
@router.get("/{table_name}")
def list_rows(
    table_name: str,
    search:     Optional[str] = Query(None, description="Keyword search across all string columns"),
    sort_by:    Optional[str] = Query(None, description="Column name to sort by"),
    sort_order: str           = Query("asc",  description="'asc' or 'desc'"),
    limit:      int           = Query(500,   ge=1, le=5000),
    offset:     int           = Query(0,     ge=0),
    # chicago_crime specific filters
    year:       Optional[int]  = Query(None),
    arrest:     Optional[bool] = Query(None),
    domestic:   Optional[bool] = Query(None),
    district:   Optional[int]  = Query(None),
    community:  Optional[int]  = Query(None),
    db: Session = Depends(get_db),
):
    model, pk_attr, *_ = _resolve(table_name)
    q = db.query(model)

    # Global keyword search across string columns
    if search:
        str_cols = _get_string_cols(model)
        conditions = [
            getattr(model, col).ilike(f"%{search}%")
            for col in str_cols
        ]
        if conditions:
            q = q.filter(or_(*conditions))

    # chicago_crime specific column filters
    if table_name == "chicago_crime":
        if year      is not None: q = q.filter(ChicagoCrime.Year         == year)
        if arrest    is not None: q = q.filter(ChicagoCrime.arrest       == arrest)
        if domestic  is not None: q = q.filter(ChicagoCrime.domestic     == domestic)
        if district  is not None: q = q.filter(ChicagoCrime.district_code == district)
        if community is not None: q = q.filter(ChicagoCrime.community_code == community)

    # Sorting
    if sort_by:
        col = getattr(model, sort_by, None)
        if col is None:
            raise HTTPException(status_code=400, detail=f"Column '{sort_by}' not found in {table_name}")
        q = q.order_by(asc(col) if sort_order.lower() != "desc" else desc(col))

    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    return {"total": total, "rows": [_row_to_dict(r) for r in rows]}


# ── GET /api/tables/{table_name}/fk-options — FK dropdown data ────────────────
@router.get("/{table_name}/fk-options")
def fk_options(table_name: str, db: Session = Depends(get_db)):
    """Returns valid PK+label pairs for FK dropdowns in Add/Modify forms."""
    if table_name == "chicago_crime":
        return {
            "iucr_codes":       [{"iucr": r.iucr, "label": f"{r.iucr} — {r.primary_type}"}
                                  for r in db.query(IUCRCode).order_by(IUCRCode.iucr).all()],
            "city_community":   [{"community_code": r.community_code, "label": f"{r.community_code} — {r.community_name}"}
                                  for r in db.query(CityCommunity).order_by(CityCommunity.community_code).all()],
            "district_ps_info": [{"district_code": r.district_code, "label": f"{r.district_code} — {r.district_name}"}
                                  for r in db.query(DistrictPSInfo).order_by(DistrictPSInfo.district_code).all()],
            "police_beat_info": [{"beat_num": r.beat_num}
                                  for r in db.query(PoliceBeatInfo).order_by(PoliceBeatInfo.beat_num).all()],
            "ward_office":      [{"ward": r.ward, "label": f"Ward {r.ward} — {r.alderman}"}
                                  for r in db.query(WardOffice).order_by(WardOffice.ward).all()],
        }
    return {}


# ── GET /api/tables/{table_name}/{pk} — Fetch single record by PK ─────────────
@router.get("/{table_name}/{pk}")
def get_row(table_name: str, pk: str, db: Session = Depends(get_db)):
    model, pk_attr, _, _, ReadSchema = _resolve(table_name)
    pk_col = getattr(model, pk_attr)
    # Cast PK to the column's Python type
    pk_type = pk_col.property.columns[0].type
    try:
        typed_pk = int(pk) if not isinstance(pk_type, String) else pk
    except ValueError:
        raise HTTPException(status_code=422, detail=f"PK '{pk}' must be an integer for {table_name}")

    row = db.query(model).filter(pk_col == typed_pk).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Record with {pk_attr}={pk} not found in {table_name}")
    return _row_to_dict(row)


# ── POST /api/tables/{table_name} — Create new record ─────────────────────────
@router.post("/{table_name}", status_code=201)
def create_row(table_name: str, payload: dict[str, Any], db: Session = Depends(get_db)):
    model, pk_attr, CreateSchema, _, _ = _resolve(table_name)
    # Validate via Create schema
    validated = CreateSchema(**payload)
    data = validated.model_dump(exclude_none=False)
    row = model(**data)
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except sqlexc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Integrity error: {e.orig}")
    return {"message": "Record created successfully.", "data": _row_to_dict(row)}


# ── PUT /api/tables/{table_name}/{pk} — Update existing record ────────────────
@router.put("/{table_name}/{pk}")
def update_row(table_name: str, pk: str, payload: dict[str, Any], db: Session = Depends(get_db)):
    model, pk_attr, _, UpdateSchema, _ = _resolve(table_name)
    pk_col = getattr(model, pk_attr)
    pk_type = pk_col.property.columns[0].type
    typed_pk = int(pk) if not isinstance(pk_type, String) else pk

    row = db.query(model).filter(pk_col == typed_pk).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Record with {pk_attr}={pk} not found in {table_name}")

    validated = UpdateSchema(**payload)
    updates = validated.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(row, field, value)
    try:
        db.commit()
        db.refresh(row)
    except sqlexc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Integrity error: {e.orig}")
    return {"message": "Record updated successfully.", "data": _row_to_dict(row)}


# ── DELETE /api/tables/{table_name}/{pk} — Delete a record ───────────────────
@router.delete("/{table_name}/{pk}")
def delete_row(table_name: str, pk: str, db: Session = Depends(get_db)):
    model, pk_attr, *_ = _resolve(table_name)
    pk_col = getattr(model, pk_attr)
    pk_type = pk_col.property.columns[0].type
    typed_pk = int(pk) if not isinstance(pk_type, String) else pk

    row = db.query(model).filter(pk_col == typed_pk).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Record with {pk_attr}={pk} not found in {table_name}")

    snapshot = _row_to_dict(row)
    try:
        db.delete(row)
        db.commit()
    except sqlexc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409,
                            detail=f"Cannot delete: record is referenced by child rows. ({e.orig})")
    return {"message": f"Record {pk_attr}={pk} deleted successfully.", "deleted": snapshot}
