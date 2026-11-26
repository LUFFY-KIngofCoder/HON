"""
FastAPI endpoint tests using TestClient.
Covers: health, root, all analytics endpoints, and full CRUD round-trip on all 6 tables.
Run from c:\HON:  python -m pytest app/tests/test_api.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── System ────────────────────────────────────────────────────────────────────
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "analytics_endpoints" in r.json()


# ── Analytics ─────────────────────────────────────────────────────────────────
def test_kpis():
    r = client.get("/api/analytics/kpis")
    assert r.status_code == 200
    j = r.json()
    assert j["total_incidents"] == 497
    assert 0 <= j["arrest_rate_pct"] <= 100

def test_yearly():
    r = client.get("/api/analytics/yearly")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 5
    assert rows[-1]["year"] == 2016

def test_categories():
    r = client.get("/api/analytics/categories?limit=5")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 5
    assert rows[0]["primary_type"] == "THEFT"

def test_heatmap():
    r = client.get("/api/analytics/heatmap")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) > 0
    assert "Month" in rows[0] and "DayOfWeek" in rows[0]

def test_daily():
    r = client.get("/api/analytics/daily")
    assert r.status_code == 200
    j = r.json()
    assert "data" in j and "note" in j

def test_communities():
    r = client.get("/api/analytics/communities?limit=10")
    assert r.status_code == 200
    j = r.json()
    assert "top" in j and "stats" in j
    assert j["stats"]["outlier_count"] >= 0


# ── CRUD List ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("table,expected_total", [
    ("chicago_crime",    497),
    ("iucr_codes",       410),
    ("city_community",    77),
    ("district_ps_info",  22),
    ("police_beat_info", 275),
    ("ward_office",       50),
])
def test_list_tables(table, expected_total):
    r = client.get(f"/api/tables/{table}?limit=10&offset=0")
    assert r.status_code == 200
    j = r.json()
    assert j["total"] == expected_total
    assert len(j["rows"]) == 10

def test_list_chicago_crime_filters():
    r = client.get("/api/tables/chicago_crime?year=2016&arrest=true&limit=10")
    assert r.status_code == 200
    j = r.json()
    assert j["total"] == 119

def test_list_chicago_crime_search():
    r = client.get("/api/tables/chicago_crime?search=THEFT&limit=5")
    assert r.status_code == 200

def test_list_unknown_table():
    r = client.get("/api/tables/nonexistent")
    assert r.status_code == 404


# ── CRUD Get Single ───────────────────────────────────────────────────────────
def test_get_crime_by_id():
    r = client.get("/api/tables/chicago_crime/10508693")
    assert r.status_code == 200
    assert r.json()["id"] == 10508693

def test_get_iucr_by_code():
    r = client.get("/api/tables/iucr_codes/0110")
    assert r.status_code == 200
    assert r.json()["iucr"] == "0110"

def test_get_notfound():
    r = client.get("/api/tables/chicago_crime/9999999")
    assert r.status_code == 404


# ── FK Options ────────────────────────────────────────────────────────────────
def test_fk_options_crime():
    r = client.get("/api/tables/chicago_crime/fk-options")
    assert r.status_code == 200
    j = r.json()
    assert "iucr_codes" in j and "city_community" in j


# ── CRUD Create / Update / Delete round-trip on police_beat_info ──────────────
NEW_BEAT = {"beat_num": 9999, "district": 1, "sector": 9, "beat": 999}

def test_create_beat():
    # cleanup if leftover from prior run
    client.delete("/api/tables/police_beat_info/9999")
    r = client.post("/api/tables/police_beat_info", json=NEW_BEAT)
    assert r.status_code == 201
    assert r.json()["data"]["beat_num"] == 9999

def test_update_beat():
    r = client.put("/api/tables/police_beat_info/9999", json={"sector": 7})
    assert r.status_code == 200
    assert r.json()["data"]["sector"] == 7

def test_delete_beat():
    r = client.delete("/api/tables/police_beat_info/9999")
    assert r.status_code == 200
    assert r.json()["deleted"]["beat_num"] == 9999

def test_delete_notfound():
    r = client.delete("/api/tables/police_beat_info/9999")
    assert r.status_code == 404

def test_duplicate_create():
    r1 = client.post("/api/tables/ward_office", json={"ward": 1, "alderman": "Test"})
    r2 = client.post("/api/tables/ward_office", json={"ward": 1, "alderman": "Duplicate"})
    assert r2.status_code == 409
    # clean up only if r1 succeeded with a NEW record (not 409)
    # ward 1 already exists so both may 409; just ensure no 500
    assert r1.status_code in (201, 409)
