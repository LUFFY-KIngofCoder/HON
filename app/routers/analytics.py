"""
Analytics Router — read-only endpoints that power the Dashboard.
Queries vw_crime_yearly, vw_crime_by_category, and chicago_crime directly.
"""

from __future__ import annotations
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ── KPI Summary ───────────────────────────────────────────────────────────────
@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """
    Returns top-level KPIs for the police dashboard header strip:
    total_incidents, total_arrests, arrest_rate_pct,
    domestic_incidents, domestic_rate_pct, active_communities.
    """
    row = db.execute(text("""
        SELECT
            COUNT(*)                                                   AS total_incidents,
            SUM(CASE WHEN arrest = 1 THEN 1 ELSE 0 END)               AS total_arrests,
            ROUND(AVG(CASE WHEN arrest = 1 THEN 100.0 ELSE 0 END), 2) AS arrest_rate_pct,
            SUM(CASE WHEN domestic = 1 THEN 1 ELSE 0 END)             AS domestic_incidents,
            ROUND(AVG(CASE WHEN domestic = 1 THEN 100.0 ELSE 0 END),2)AS domestic_rate_pct,
            COUNT(DISTINCT community_code)                             AS active_communities
        FROM chicago_crime
    """)).mappings().one()
    return dict(row)


# ── Yearly Trend ──────────────────────────────────────────────────────────────
@router.get("/yearly")
def get_yearly(db: Session = Depends(get_db)):
    """
    Returns yearly total_crimes, total_arrests, arrest_rate_pct
    from vw_crime_yearly (sorted ascending by year).
    """
    rows = db.execute(text("SELECT * FROM vw_crime_yearly ORDER BY year")).mappings().all()
    return [dict(r) for r in rows]


# ── Crime by Category ─────────────────────────────────────────────────────────
@router.get("/categories")
def get_categories(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns top N crime categories from vw_crime_by_category:
    primary_type, crime_count, total_arrests, arrest_rate_pct, pct_of_total.
    """
    rows = db.execute(text(
        f"SELECT * FROM vw_crime_by_category ORDER BY crime_count DESC LIMIT {limit}"
    )).mappings().all()
    return [dict(r) for r in rows]


# ── Month × Day-of-Week Heatmap ───────────────────────────────────────────────
@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    """
    Returns crime frequency pivoted by Month (1–12) × DayOfWeek
    for the operational heatmap.
    """
    rows = db.execute(text("""
        SELECT Month, DayOfWeek, COUNT(*) AS crime_count
        FROM chicago_crime
        GROUP BY Month, DayOfWeek
        ORDER BY Month, DayOfWeek
    """)).mappings().all()
    return [dict(r) for r in rows]


# ── Daily Distribution (Days 1–31) ────────────────────────────────────────────
@router.get("/daily")
def get_daily(db: Session = Depends(get_db)):
    """
    Returns crime counts by Day-of-month (1-31).
    Includes note about the dataset's 00:00:00 timestamp limitation.
    """
    rows = db.execute(text("""
        SELECT Day, COUNT(*) AS crime_count
        FROM chicago_crime
        WHERE Day IS NOT NULL
        GROUP BY Day
        ORDER BY Day
    """)).mappings().all()
    return {
        "data": [dict(r) for r in rows],
        "note": "All records share 00:00:00 timestamps — hourly granularity is not available in this dataset."
    }


# ── Community Hotspots & IQR Stats ───────────────────────────────────────────
@router.get("/communities")
def get_communities(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns top N communities by crime count joined with community names,
    plus NumPy-computed IQR statistics and outlier flagging.
    """
    rows = db.execute(text("""
        SELECT
            c.community_code,
            COALESCE(m.community_name, 'Community ' || c.community_code) AS community_name,
            COUNT(*) AS crime_count
        FROM chicago_crime c
        LEFT JOIN city_community m ON c.community_code = m.community_code
        WHERE c.community_code IS NOT NULL
        GROUP BY c.community_code
        ORDER BY crime_count DESC
    """)).mappings().all()

    all_counts = np.array([r["crime_count"] for r in rows], dtype=float)
    q1, q3 = float(np.percentile(all_counts, 25)), float(np.percentile(all_counts, 75))
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr

    top_rows = [dict(r) for r in rows[:limit]]
    for row in top_rows:
        row["is_outlier"] = row["crime_count"] > upper_fence

    # All outlier communities
    outliers = [
        {
            "community_code": r["community_code"],
            "community_name": r["community_name"],
            "crime_count": r["crime_count"],
            "distance_above_fence": round(r["crime_count"] - upper_fence, 2)
        }
        for r in rows if r["crime_count"] > upper_fence
    ]

    return {
        "top": top_rows,
        "outliers": outliers,
        "all_counts": [float(c) for c in all_counts],
        "stats": {
            "mean":          round(float(np.mean(all_counts)), 2),
            "median":        round(float(np.median(all_counts)), 2),
            "std":           round(float(np.std(all_counts)), 2),
            "min":           round(float(np.min(all_counts)), 2),
            "max":           round(float(np.max(all_counts)), 2),
            "q1":            round(q1, 2),
            "q3":            round(q3, 2),
            "iqr":           round(iqr, 2),
            "upper_fence":   round(upper_fence, 2),
            "outlier_count": len(outliers),
        }
    }


# ── Crime Cross-Correlation Matrix ────────────────────────────────────────────
@router.get("/correlation")
def get_correlation(db: Session = Depends(get_db)):
    """
    Computes Pearson cross-correlation matrix across numeric features
    and lists strong correlated pairs (|r| >= 0.6) and correlations with arrest.
    """
    import pandas as pd
    df = pd.read_sql("SELECT * FROM chicago_crime", db.bind)

    numeric_cols = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'int32', float, bool] and col not in ['id', 'Hour']:
            numeric_cols.append(col)

    df_corr = df[numeric_cols].copy()
    if 'arrest' in df_corr.columns:
        df_corr['arrest'] = df_corr['arrest'].astype(int)
    if 'domestic' in df_corr.columns:
        df_corr['domestic'] = df_corr['domestic'].astype(int)

    corr = df_corr.corr()

    # Mask self and symmetric pairs to find strong correlations
    strong_pairs = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            f1, f2 = corr.columns[i], corr.columns[j]
            r_val = float(corr.iloc[i, j])
            if abs(r_val) >= 0.6:
                strong_pairs.append({
                    "feature_1": f1,
                    "feature_2": f2,
                    "correlation": round(r_val, 3)
                })

    strong_pairs = sorted(strong_pairs, key=lambda x: abs(x["correlation"]), reverse=True)

    arrest_corrs = []
    if 'arrest' in corr.columns:
        s = corr['arrest'].drop('arrest').sort_values(ascending=False)
        arrest_corrs = [
            {"feature": feat, "correlation_with_arrest": round(float(val), 3)}
            for feat, val in s.items()
        ]

    return {
        "columns": corr.columns.tolist(),
        "matrix": [[round(float(val), 3) if not np.isnan(val) else 0.0 for val in row] for row in corr.values],
        "strong_pairs": strong_pairs,
        "arrest_correlations": arrest_corrs
    }

