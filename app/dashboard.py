"""
Streamlit Web Application: Chicago Crime Analytics & Police Operations Hub
Complete Dashboard covering all analytical visualizations from Use Cases 1, 2, 3, and 4
in a single, continuous, seamlessly scrollable page (no nested tabs for graphs).
Run command:
    streamlit run app/dashboard.py
"""

import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="Chicago Police Department — Intelligence & Analytics Hub",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 14px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .section-header {
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 8px;
        margin-top: 24px;
        margin-bottom: 16px;
        color: #1e3d59;
    }
</style>
""", unsafe_allow_html=True)


# Helper function to query backend API
def fetch_api(endpoint: str, params=None):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        st.error(f"API Error ({r.status_code}): {r.text}")
        return None
    except requests.exceptions.ConnectionError:
        st.warning(f"⚠️ Cannot connect to backend API at {API_BASE_URL}. Ensure FastAPI is running (`uvicorn app.main:app`).")
        return None
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return None


# Sidebar Navigation
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Chicago%2C_Illinois.svg/320px-Flag_of_Chicago%2C_Illinois.svg.png", width=120)
st.sidebar.title("CPD Intelligence Hub")
st.sidebar.caption("Chicago Police Department Data Analytics & Operations")
st.sidebar.divider()

nav_choice = st.sidebar.radio(
    "Select Interface Mode:",
    ["📊 Full Analytics Dashboard", "🗄️ Relational Data Management"],
    index=0
)

st.sidebar.divider()
st.sidebar.info(
    "💡 **All-in-One Dashboard Coverage**\n"
    "- **Section 1:** Executive KPI Summary\n"
    "- **Section 2:** Annual Trend & 2016 Outlier Skew\n"
    "- **Section 3:** Crime Categories & Arrest Outcomes\n"
    "- **Section 4:** Temporal Heatmap & 24h/31d Distribution\n"
    "- **Section 5:** Community Hotspots & IQR Outlier Models\n"
    "- **Section 6:** Pearson Cross-Correlation Matrix\n"
    "- **Section 7:** 2×2 SQL Stored Views Grid"
)


# ==============================================================================
# INTERFACE 1: COMPREHENSIVE ALL-IN-ONE SCROLLABLE DASHBOARD
# ==============================================================================
if nav_choice == "📊 Full Analytics Dashboard":
    st.title("🏙️ Chicago Crime Operations & Analytics Hub")
    st.markdown("Comprehensive operational intelligence compiling all visual models and statistical patterns from Use Cases 1 through 4 on a single scrollable dashboard.")

    # --------------------------------------------------------------------------
    # SECTION 1: EXECUTIVE KPI SUMMARY
    # --------------------------------------------------------------------------
    kpis = fetch_api("/api/analytics/kpis")
    if kpis:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Incidents", f"{kpis['total_incidents']:,}")
        c2.metric("Total Arrests", f"{kpis['total_arrests']:,}")
        c3.metric("Arrest Clearance Rate", f"{kpis['arrest_rate_pct']:.1f}%")
        c4.metric("Domestic Violence", f"{kpis['domestic_rate_pct']:.1f}%", f"{kpis['domestic_incidents']:,} incidents")
        c5.metric("Active Communities", f"{kpis['active_communities']} / 77")
        st.divider()

    yearly_data = fetch_api("/api/analytics/yearly")
    cat_data = fetch_api("/api/analytics/categories?limit=10")
    heat_data = fetch_api("/api/analytics/heatmap")
    daily_res = fetch_api("/api/analytics/daily")
    comm_res = fetch_api("/api/analytics/communities?limit=10")
    corr_res = fetch_api("/api/analytics/correlation")

    # --------------------------------------------------------------------------
    # USE CASE 1: LOAD AND CLEAN CHICAGO CRIME DATA (Q2 Date Skew & Outliers)
    # --------------------------------------------------------------------------
    st.markdown("### 📦 Use Case 1 — Load & Clean Chicago Crime Data (Date Distribution & Skew)")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        # UC1 Question 2: Yearly Histogram
        if yearly_data:
            df_y = pd.DataFrame(yearly_data)
            fig, ax = plt.subplots(figsize=(8, 4.5))
            bars_hist = ax.bar(df_y['year'].astype(str), df_y['total_crimes'], color='steelblue', edgecolor='black', width=0.65)
            for bar in bars_hist:
                h = bar.get_height()
                ax.annotate(f"{int(h)}", (bar.get_x() + bar.get_width()/2, h + 8), ha='center', fontweight='bold', fontsize=9.5)
            ax.set_title("Distribution of Incidents by Year (Histogram)", fontweight='bold', fontsize=12, pad=10)
            ax.set_xlabel("Year")
            ax.set_ylabel("Frequency (Number of Incidents)")
            ax.set_ylim(0, df_y['total_crimes'].max() * 1.15)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** 2016 completely dominates the dataset with **489 out of 497 records (98.4%)**. Years 2012–2015 contribute only 1–3 records each — these are historical back-entries, not full-year data, making 2016 the only analytically representative year.")

    with col_t2:
        # UC1 Question 2: Year Box Plot confirming extreme skew towards 2016
        if yearly_data:
            df_y = pd.DataFrame(yearly_data)
            years_expanded = []
            for _, r in df_y.iterrows():
                years_expanded.extend([r['year']] * int(r['total_crimes']))
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.boxplot(years_expanded, vert=False, patch_artist=True,
                       boxprops=dict(facecolor='lightblue', color='navy'),
                       medianprops=dict(color='red', linewidth=2.5))
            ax.set_title("Year Box Plot (Empirical Proof of 2016 Skew)", fontweight='bold', fontsize=12, pad=10)
            ax.set_xlabel("Year")
            ax.set_yticks([])
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** The box plot's median sits at **2016** and the whiskers barely reach back to 2012. This visually proves the extreme right skew — the distribution is not spread across years; it is almost entirely a single-year snapshot of Chicago crime in 2016.")

    st.caption("ℹ️ **Data Diagnostic Note:** 2016 represents **98.4%** of all records (489 / 497). Years 2012–2015 act as statistical outliers representing historical back-entries.")
    st.divider()

    # --------------------------------------------------------------------------
    # USE CASE 2: EXPLORATORY ANALYSIS & VISUALIZATION OF CRIME
    # --------------------------------------------------------------------------
    st.markdown("### 📊 Use Case 2 — Exploratory Analysis & Visualization of Crime")

    # UC2 Row 1: Annual Crime Trend & Top 10 Categories
    col_u2_1, col_u2_2 = st.columns(2)
    with col_u2_1:
        if yearly_data:
            df_y = pd.DataFrame(yearly_data)
            fig, ax = plt.subplots(figsize=(8, 5.2))
            ax.plot(df_y['year'], df_y['total_crimes'], marker='o', color='#1f77b4', linewidth=2.5, markersize=8)
            for _, r in df_y.iterrows():
                pct = r['total_crimes'] / df_y['total_crimes'].sum() * 100
                ax.annotate(f"{int(r['total_crimes'])}\n({pct:.1f}%)", (r['year'], r['total_crimes']),
                            textcoords='offset points', xytext=(0, 8), ha='center', fontweight='bold', fontsize=9)
            ax.set_title("Task 1: Annual Crime Trend (2012–2016)", fontweight='bold', fontsize=12, pad=12)
            ax.set_xlabel("Year")
            ax.set_ylabel("Reported Incidents")
            ax.set_xticks(df_y['year'])
            ax.set_ylim(0, df_y['total_crimes'].max() * 1.18)
            ax.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** Crime volume is essentially flat from 2012–2015 (1–3 incidents each) then surges to **489 in 2016 (98.4%)**. The apparent upward trend is purely a data-collection artifact — 2016 is the primary recording year, not evidence of a crime spike.")

    with col_u2_2:
        # UC2 Task 2: Top 10 Crime Types Horizontal Bar
        if cat_data:
            df_c = pd.DataFrame(cat_data).sort_values("crime_count", ascending=True)
            fig, ax = plt.subplots(figsize=(8, 5.2))
            palette = sns.color_palette("Blues_r", len(df_c))
            bars = ax.barh(df_c['primary_type'], df_c['crime_count'], color=palette[::-1], edgecolor='black')
            for bar, pct in zip(bars, df_c['pct_of_total']):
                w_val = bar.get_width()
                ax.annotate(f"{int(w_val)} ({pct:.1f}%)", (w_val, bar.get_y() + bar.get_height()/2),
                            xytext=(5, 0), textcoords="offset points", va="center", fontsize=8.5, fontweight='bold')
            ax.set_title("Task 2: Top 10 Crime Categories (Primary Type)", fontweight='bold', fontsize=12, pad=12)
            ax.set_xlabel("Number of Incidents", fontsize=10)
            ax.set_xlim(0, df_c['crime_count'].max() * 1.25)
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** **Theft (21.1%)** and **Battery (17.1%)** alone account for over 1 in 3 crimes. The top 3 categories (Theft, Battery, Criminal Damage) represent **48%** of all incidents — a classic Pareto pattern where a small number of crime types drive the majority of police workload.")

    # UC2 Row 2: Arrest Outcome Donut & Month vs DayOfWeek Heatmap
    col_u2_3, col_u2_4 = st.columns(2)
    with col_u2_3:
        # UC2 Task 3: Arrest Outcome Donut Chart
        if kpis:
            tot_arr = kpis['total_arrests']
            tot_no = kpis['total_incidents'] - tot_arr
            fig, ax = plt.subplots(figsize=(8, 5.2))
            wedges, texts, autotexts = ax.pie(
                [tot_arr, tot_no],
                labels=['Arrest Made', 'No Arrest'],
                autopct='%1.1f%%',
                startangle=140,
                colors=['#2ca02c', '#d62728'],
                explode=(0.06, 0),
                wedgeprops=dict(width=0.6, edgecolor='black'),
                textprops=dict(fontsize=10)
            )
            for autotext in autotexts:
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            ax.set_title(f"Task 3: Overall Arrest Rate: {kpis['arrest_rate_pct']:.2f}%\n({tot_arr} / {kpis['total_incidents']})", fontweight='bold', fontsize=12, pad=12)
            # Lock the pie to a fixed radius so it never expands to fill the full canvas
            ax.set_xlim(-1.35, 1.35)
            ax.set_ylim(-1.35, 1.35)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** Only **1 in 4 crimes (24.9%)** results in an arrest. This low clearance rate suggests that most crimes — especially Theft and Criminal Damage — are reported but go unresolved, pointing to resource constraints or insufficient evidence at the scene.")

    with col_u2_4:
        # UC2 Task 4: Heatmap Month vs DayOfWeek
        if heat_data:
            df_heat = pd.DataFrame(heat_data)
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot = df_heat.pivot(index='DayOfWeek', columns='Month', values='crime_count').reindex(days_order).fillna(0)
            fig, ax = plt.subplots(figsize=(8, 5.0))
            sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".0f", cbar_kws={'label': 'Incidents'}, ax=ax)
            ax.set_title("Task 4: Crime Frequency Heatmap (Month vs. Day)", fontweight='bold', fontsize=12, pad=12)
            ax.set_xlabel("Month of Year")
            ax.set_ylabel("Day of Week")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** Only months **1, 2, 3, 4, 5, and 11** have recorded data — the remaining months are absent entirely. This is a direct consequence of the dataset's narrow date range: the 2016 records are concentrated in early-to-mid year. **May (Month 5)** dominates the heatmap with the highest cell values, particularly on Tuesday and Wednesday, meaning the majority of this dataset's incidents occurred in May 2016 on those two weekdays. No summer-peak or weekend-peak pattern can be reliably concluded from this incomplete month coverage.")

    # UC2 Row 3: Task 5 Top 10 Community Areas
    if comm_res:
        df_comm = pd.DataFrame(comm_res['top']).sort_values("crime_count", ascending=True)
        fig, ax = plt.subplots(figsize=(14, 4.5))
        palette = sns.color_palette('Blues_r', len(df_comm))
        bars = ax.barh(df_comm['community_name'], df_comm['crime_count'], color=palette[::-1], edgecolor='black')
        for bar in bars:
            w = bar.get_width()
            pct = w / kpis['total_incidents'] * 100 if kpis else 0
            ax.annotate(f"{int(w)} ({pct:.1f}%)", (w + 0.5, bar.get_y() + bar.get_height()/2),
                        va='center', ha='left', fontsize=8.5, fontweight='bold')
        ax.set_title("Task 5: Top 10 Chicago Community Areas with Highest Crime", fontweight='bold', fontsize=12, pad=10)
        ax.set_xlabel("Number of Incidents")
        ax.set_xlim(0, df_comm['crime_count'].max() + 5)
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.caption("📌 **Insight:** The top 10 community areas account for a disproportionate share of total crime. The leading communities are concentrated on Chicago's South and West sides — historically underserved areas with higher poverty rates and unemployment, reinforcing the socioeconomic link to crime concentration.")

    st.divider()

    # --------------------------------------------------------------------------
    # USE CASE 3: STATISTICAL INSIGHTS & PATTERN DETECTION
    # --------------------------------------------------------------------------
    st.markdown("### 📈 Use Case 3 — Statistical Insights & Pattern Detection")

    # UC3 Task 1: 24-Hour & 31-Day Temporal Distribution
    col_u3_1, col_u3_2 = st.columns(2)
    with col_u3_1:
        hourly_counts = np.zeros(24)
        hourly_counts[0] = kpis['total_incidents'] if kpis else 497
        fig, ax_h = plt.subplots(figsize=(8, 4.6))
        ax_h.fill_between(range(24), hourly_counts, color='#1f77b4', alpha=0.25)
        ax_h.plot(range(24), hourly_counts, marker='o', linewidth=2.5, color='#1f77b4', markersize=5, label='Crimes / Hour')
        ax_h.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='Midnight Spike (100%)')
        ax_h.annotate(
            '100% at 00:00:00\n(No HH:MM in CSV)',
            xy=(0, hourly_counts[0]),
            xytext=(3, hourly_counts[0] * 0.8),
            arrowprops=dict(facecolor='red', shrink=0.08, width=1.5, headwidth=7),
            fontweight='bold', fontsize=9, color='darkred'
        )
        ax_h.set_title('Task 1a: Hourly Crime Intensity (00:00–23:00)', fontweight='bold', fontsize=12, pad=10)
        ax_h.set_xlabel('Hour of Day')
        ax_h.set_ylabel('Reported Crimes')
        ax_h.set_xticks(range(0, 24, 3))
        ax_h.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 3)])
        ax_h.set_ylim(-15, max(hourly_counts) * 1.15)
        ax_h.grid(True, linestyle='--', alpha=0.5)
        ax_h.legend(loc='upper right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.caption("📌 **Insight:** **100% of records spike at midnight (00:00:00)** because the source CSV stores only dates with no time component — the time defaults to midnight on import. This is a data-quality artifact, not a real crime pattern. No meaningful hourly analysis is possible without raw HH:MM data.")

    with col_u3_2:
        if daily_res:
            df_day = pd.DataFrame(daily_res['data'])
            daily_series = pd.Series(0, index=range(1, 32))
            for _, r in df_day.iterrows():
                if 1 <= int(r['Day']) <= 31:
                    daily_series[int(r['Day'])] = r['crime_count']

            fig, ax = plt.subplots(figsize=(8, 4.6))
            ax.bar(daily_series.index, daily_series.values, color='#2ca02c', edgecolor='black', alpha=0.8, width=0.75)
            ax.plot(daily_series.index, daily_series.values, color='darkgreen', marker='o', linewidth=1.8, markersize=4)
            for d in [3, 4, 1]:
                if d in daily_series and daily_series[d] > 0:
                    cnt = daily_series[d]
                    ax.text(d, cnt + 7, f'Day {d}\n({cnt})', ha='center', va='bottom', fontweight='bold', fontsize=8.5)
            ax.set_title("Task 1b: Daily Crime Distribution (Days 1–31)", fontweight='bold', fontsize=12, pad=10)
            ax.set_xlabel("Day of Month (1 to 31)")
            ax.set_ylabel("Reported Crimes")
            ax.set_xticks(range(1, 32, 2))
            ax.set_xlim(0, 32)
            ax.set_ylim(0, max(daily_series.values) * 1.18)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** Days **3 and 4** show the highest incident counts, while **Day 31** naturally drops. The distribution is relatively uniform across the month — no strong days-of-month pattern emerges, suggesting crimes are not clustered around paydays or other calendar events.")

    # UC3 Task 2: Community Area IQR Box Plot & Outliers
    if comm_res:
        stats = comm_res['stats']
        counts = comm_res.get('all_counts', [])
        outliers = comm_res.get('outliers', [])

        col_u3_3, col_u3_4 = st.columns(2)
        with col_u3_3:
            fig, ax = plt.subplots(figsize=(8, 4.5))
            if counts:
                ax.boxplot(
                    counts,
                    vert=False,
                    patch_artist=True,
                    boxprops=dict(facecolor='lightblue', color='navy', alpha=0.7),
                    medianprops=dict(color='red', linewidth=2.5),
                    whiskerprops=dict(color='navy', linewidth=1.5),
                    capprops=dict(color='navy', linewidth=1.5),
                    flierprops=dict(marker='o', markerfacecolor='red', markeredgecolor='black', markersize=7)
                )
            ax.axvline(stats['upper_fence'], color='darkorange', linestyle='--', linewidth=1.5, label=f"Upper Fence ({stats['upper_fence']:.1f})")
            ax.set_title("Task 2a: Community Area Crime Box Plot (IQR)", fontweight='bold', fontsize=12, pad=10)
            ax.set_xlabel("Number of Recorded Crimes")
            ax.set_yticks([])
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            ax.legend(loc='upper right')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            st.caption("📌 **Insight:** The IQR box spans roughly **3 to 9 crimes** per community area with a median of ~5–6, and whiskers extend out to ~16 — meaning the **majority of Chicago community areas recorded between 1 and 16 crimes**. The upper IQR fence sits at **18.0**. Only **3 community areas** cross that threshold and appear as red outlier dots: two at ~20 crimes and one at ~34 crimes. Those two communities are statistically anomalous — not just above average, but mathematically extreme relative to the rest of the city.")

        with col_u3_4:
            if outliers:
                plot_names = [o['community_name'] for o in outliers] + ['Upper Fence', 'Community Mean']
                plot_vals = [o['crime_count'] for o in outliers] + [stats['upper_fence'], stats['mean']]
                bar_colors = ['#d62728', '#e377c2', '#e377c2', 'darkorange', '#1f77b4'][:len(plot_names)]

                fig, ax_out = plt.subplots(figsize=(8, 4.5))
                bars = ax_out.barh(plot_names[::-1], plot_vals[::-1], color=bar_colors[::-1], edgecolor='black')
                for bar in bars:
                    ax_out.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.1f}',
                                va='center', ha='left', fontweight='bold', fontsize=9.5)
                ax_out.set_title("Task 2b: Statistical Outliers vs. IQR Upper Fence", fontweight='bold', fontsize=12, pad=10)
                ax_out.set_xlabel("Crime Count / Threshold")
                ax_out.set_xlim(0, max(plot_vals) + 5)
                ax_out.grid(axis='x', linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                st.caption("📌 **Insight:** The outlier communities sit **well above the IQR upper fence**, confirming they are statistically anomalous, not just above-average. These are genuine crime hotspots requiring targeted policing strategy. The gap between the top outlier and the upper fence quantifies how extreme the concentration is.")

    # UC3 Task 3: Cross-Correlation Matrix
    if corr_res:
        corr_cols = corr_res['columns']
        corr_mat = np.array(corr_res['matrix'])

        fig, ax_corr = plt.subplots(figsize=(11, 7.2))
        mask = np.triu(np.ones_like(corr_mat, dtype=bool))
        sns.heatmap(
            corr_mat,
            mask=mask,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            vmin=-1.0,
            vmax=1.0,
            center=0,
            square=True,
            linewidths=0.5,
            xticklabels=corr_cols,
            yticklabels=corr_cols,
            cbar_kws={'shrink': 0.8, 'label': 'Pearson Correlation (r)'},
            ax=ax_corr
        )
        ax_corr.set_title("Task 3: Crime Feature Pairwise Cross-Correlation Matrix", fontweight='bold', fontsize=12, pad=10)
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.caption("📌 **Insight:** The dominant correlations are entirely **geographic and administrative** — not behavioral. `district_code` ↔ `beat_num` = **1.00** (beats are defined sub-units of districts, so they move in perfect lockstep). `latitude` ↔ `y_coordinate` = **1.00** (same geographic position in two coordinate systems). `community_code` ↔ `y_coordinate` = **−0.74** (northern Chicago communities carry lower code numbers — a city-numbering convention). Most importantly, **`arrest` correlates near-zero with every single feature** (highest is `Day` at 0.19, `Month` at −0.18) — meaning no geographic or temporal variable in this dataset can predict whether an arrest will be made. Arrest outcome appears essentially random with respect to location and time.")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Top Strongest Correlations (|r| >= 0.6):**")
            st.dataframe(pd.DataFrame(corr_res['strong_pairs']), use_container_width=True)
        with col_p2:
            st.markdown("**Pairwise Correlations with Arrest Outcome:**")
            st.dataframe(pd.DataFrame(corr_res['arrest_correlations']), use_container_width=True)

    st.divider()

    # --------------------------------------------------------------------------
    # USE CASE 4: SQL STORED VIEWS DASHBOARD
    # --------------------------------------------------------------------------
    st.markdown("### 🗄️ Use Case 4 — SQL Database Stored Views (`vw_crime_yearly` & `vw_crime_by_category`)")
    st.markdown("Reporting grid directly querying persistent SQLite views `vw_crime_yearly` and `vw_crime_by_category`.")

    if yearly_data and cat_data:
        df_vy = pd.DataFrame(yearly_data)
        df_vc = pd.DataFrame(cat_data)

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Use Case 4 — SQL View Analytics Dashboard (chicago_crime.db)", fontsize=15, fontweight="bold", y=0.98)

        # Panel 1: Yearly Volume vs. Arrest Count
        ax1 = axes[0, 0]
        x = np.arange(len(df_vy))
        w = 0.38
        bars_tot = ax1.bar(x - w/2, df_vy["total_crimes"], width=w, label="Total Crimes", color="#2b5c8f")
        bars_a   = ax1.bar(x + w/2, df_vy["total_arrests"], width=w, label="Total Arrests", color="#e07a5f")
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_vy["year"].astype(str))
        ax1.set_title("Yearly Crimes vs. Arrests (vw_crime_yearly)", fontweight="bold")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Incident Count")
        ax1.legend()
        ax1.grid(axis='y', linestyle='--', alpha=0.5)
        for bar in list(bars_tot) + list(bars_a):
            h = bar.get_height()
            ax1.annotate(f"{int(h)}", (bar.get_x() + bar.get_width()/2, h), ha="center", va="bottom", fontsize=8.5)

        # Panel 2: Yearly Arrest Rate (%)
        ax2 = axes[0, 1]
        sns.lineplot(data=df_vy, x="year", y="arrest_rate_pct", marker="o", linewidth=2.5, color="#2a9d8f", ax=ax2)
        ax2.set_title("Yearly Arrest Rate % (vw_crime_yearly)", fontweight="bold")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Arrest Rate (%)")
        ax2.set_ylim(0, 115)
        ax2.set_xticks(df_vy["year"])
        ax2.grid(True, linestyle='--', alpha=0.5)
        for _, r in df_vy.iterrows():
            ax2.annotate(f"{r['arrest_rate_pct']:.1f}%", (r["year"], r["arrest_rate_pct"]),
                         textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5, fontweight='bold')

        # Panel 3: Top 10 Crime Categories by Volume
        top10_c = df_vc.sort_values("crime_count", ascending=True)
        ax3 = axes[1, 0]
        bars_cat = ax3.barh(top10_c["primary_type"], top10_c["crime_count"], color=sns.color_palette("Blues_d", len(top10_c)))
        ax3.set_title("Top 10 Crime Categories (vw_crime_by_category)", fontweight="bold")
        ax3.set_xlabel("Crime Count")
        ax3.set_xlim(0, top10_c["crime_count"].max() * 1.25)
        ax3.grid(axis='x', linestyle='--', alpha=0.5)
        for bar, pct in zip(bars_cat, top10_c["pct_of_total"]):
            w_val = bar.get_width()
            ax3.annotate(f"{int(w_val)} ({pct:.1f}%)", (w_val, bar.get_y() + bar.get_height()/2),
                         va="center", xytext=(5, 0), textcoords="offset points", fontsize=8.5, fontweight='bold')

        # Panel 4: Arrest Rate (%) Across Top 10 Crime Categories
        top10_a = df_vc.sort_values("arrest_rate_pct", ascending=True)
        ax4 = axes[1, 1]
        bars_ar = ax4.barh(top10_a["primary_type"], top10_a["arrest_rate_pct"], color=sns.color_palette("Oranges_d", len(top10_a)))
        overall_rate = df_vy["total_arrests"].sum() * 100.0 / df_vy["total_crimes"].sum()
        ax4.axvline(overall_rate, color="crimson", linestyle="--", linewidth=1.5, label=f"Overall Avg ({overall_rate:.1f}%)")
        ax4.set_title("Arrest Rate % Across Top 10 Categories", fontweight="bold")
        ax4.set_xlabel("Arrest Rate (%)")
        ax4.set_xlim(0, max(100, top10_a["arrest_rate_pct"].max() * 1.15))
        ax4.legend(loc="lower right")
        ax4.grid(axis='x', linestyle='--', alpha=0.5)
        for bar in bars_ar:
            w_val = bar.get_width()
            ax4.annotate(f"{w_val:.1f}%", (w_val, bar.get_y() + bar.get_height()/2),
                         va="center", xytext=(5, 0), textcoords="offset points", fontsize=8.5, fontweight='bold')

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        st.pyplot(fig)
        plt.close()
        st.caption("📌 **Insight (UC4 Views):** The SQL views aggregate consistently with the raw table. Panel 1 confirms 2016's volume dominance. Panel 2 shows the **2016 arrest rate (~24%)** is the most reliable figure. Panel 3 reaffirms Theft as the top category. Panel 4 reveals **Narcotics has a disproportionately high arrest rate (~60–70%)** — likely because narcotics possession is a direct-arrest offense, unlike theft where suspects often flee.")


# ==============================================================================
# INTERFACE 2: DATA MANAGEMENT (6 TABLES CRUD)
# ==============================================================================
elif nav_choice == "🗄️ Relational Data Management":
    st.title("🗄️ Relational Data Records & CRUD Manager")
    st.markdown("Comprehensive database administration portal with sorting, filtering, and transactional CRUD operations across all 6 relational models.")

    table_options = {
        "Chicago Crime Master (chicago_crime)": ("chicago_crime", "id"),
        "IUCR Crime Codes (iucr_codes)": ("iucr_codes", "iucr"),
        "City Community Areas (city_community)": ("city_community", "community_code"),
        "District Police Stations (district_ps_info)": ("district_ps_info", "district_code"),
        "Police Beat Assignments (police_beat_info)": ("police_beat_info", "beat_num"),
        "Ward Alderman Offices (ward_office)": ("ward_office", "ward")
    }

    selected_table_label = st.selectbox("Select Target Relational Table:", list(table_options.keys()))
    table_name, pk_name = table_options[selected_table_label]

    st.divider()

    # Action Tab Navigation for CRUD
    tab_read, tab_add, tab_modify, tab_delete = st.tabs([
        "📋 Browse & Search Records",
        "➕ Add New Record",
        "✏️ Modify Existing Record",
        "🗑️ Delete Record"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: READ / BROWSE / FILTER / SORT
    # --------------------------------------------------------------------------
    with tab_read:
        st.markdown(f"### 📋 Viewing `{table_name}` Records (Primary Key: `{pk_name}`)")
        
        # Search and Sort Controls
        c_filter1, c_filter2, c_filter3 = st.columns([3, 2, 1])
        with c_filter1:
            search_query = st.text_input("🔍 Global Keyword Search (across text fields):", placeholder="e.g. THEFT, Austin, Michigan Ave")
        with c_filter2:
            sort_by_col = st.text_input("Sort By Column (Optional):", value=pk_name)
        with c_filter3:
            sort_dir = st.selectbox("Order:", ["asc", "desc"])

        # Table-specific quick filters for Crime table
        filter_params = {
            "search": search_query if search_query else None,
            "sort_by": sort_by_col if sort_by_col else None,
            "sort_order": sort_dir,
            "limit": 1000
        }

        if table_name == "chicago_crime":
            with st.expander("⚙️ Advanced Filter Options (Chicago Crime Table)"):
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    filter_year = st.selectbox("Filter Year:", [None, 2016, 2015, 2014, 2013, 2012], index=0)
                    if filter_year: filter_params["year"] = filter_year
                with fc2:
                    filter_arrest = st.selectbox("Arrest Made?:", [None, True, False], index=0)
                    if filter_arrest is not None: filter_params["arrest"] = filter_arrest
                with fc3:
                    filter_domestic = st.selectbox("Domestic Incident?:", [None, True, False], index=0)
                    if filter_domestic is not None: filter_params["domestic"] = filter_domestic

        # Fetch records
        data_res = fetch_api(f"/api/tables/{table_name}", params=filter_params)
        if data_res:
            total_records = data_res["total"]
            rows = data_res["rows"]
            st.caption(f"Showing **{len(rows)}** of **{total_records}** total records.")
            
            if rows:
                df_display = pd.DataFrame(rows)
                st.dataframe(df_display, width='stretch', height=450)
                
            else:
                st.info("No matching records found for the applied search/filter criteria.")

    # --------------------------------------------------------------------------
    # TAB 2: ADD RECORD
    # --------------------------------------------------------------------------
    with tab_add:
        st.markdown(f"### ➕ Insert New Record into `{table_name}`")
        st.markdown("Fill out the required attributes below. Foreign keys are validated against registered reference tables.")

        fk_opts = fetch_api(f"/api/tables/{table_name}/fk-options") if table_name == "chicago_crime" else {}

        with st.form(f"form_add_{table_name}", clear_on_submit=True):
            payload = {}

            if table_name == "chicago_crime":
                ca, cb = st.columns(2)
                with ca:
                    payload["case_number"] = st.text_input("Case Number * (e.g. HZ999999)")
                    payload["date"] = st.text_input("Date Timestamp", value="2016-05-15 00:00:00")
                    payload["block"] = st.text_input("Block", value="001XX N STATE ST")
                    
                    if fk_opts and "iucr_codes" in fk_opts:
                        iucr_labels = [opt["label"] for opt in fk_opts["iucr_codes"]]
                        sel_iucr = st.selectbox("IUCR Code *", iucr_labels)
                        payload["iucr_code"] = sel_iucr.split(" — ")[0]
                    else:
                        payload["iucr_code"] = st.text_input("IUCR Code * (e.g. 110)")

                    payload["location_desc"] = st.text_input("Location Description", value="STREET")
                    payload["arrest"] = st.checkbox("Arrest Made")
                    payload["domestic"] = st.checkbox("Domestic Incident")

                with cb:
                    if fk_opts and "district_ps_info" in fk_opts:
                        d_opts = [opt["label"] for opt in fk_opts["district_ps_info"]]
                        sel_d = st.selectbox("District Station", d_opts)
                        payload["district_code"] = int(sel_d.split(" — ")[0])
                    else:
                        payload["district_code"] = st.number_input("District Code", min_value=1, value=1)

                    if fk_opts and "city_community" in fk_opts:
                        c_opts = [opt["label"] for opt in fk_opts["city_community"]]
                        sel_c = st.selectbox("Community Area", c_opts)
                        payload["community_code"] = int(sel_c.split(" — ")[0])
                    else:
                        payload["community_code"] = st.number_input("Community Code", min_value=1, value=25)

                    if fk_opts and "ward_office" in fk_opts:
                        w_opts = [opt["label"] for opt in fk_opts["ward_office"]]
                        sel_w = st.selectbox("Ward Office", w_opts)
                        payload["ward_no"] = int(sel_w.split(" — ")[0].replace("Ward ", ""))
                    else:
                        payload["ward_no"] = st.number_input("Ward Number", min_value=1, value=1)

                    if fk_opts and "police_beat_info" in fk_opts:
                        b_opts = [opt["beat_num"] for opt in fk_opts["police_beat_info"]]
                        payload["beat_num"] = st.selectbox("Police Beat", b_opts)
                    else:
                        payload["beat_num"] = st.number_input("Beat Number", min_value=100, value=111)

                    payload["Year"] = st.number_input("Year *", value=2016)
                    payload["Month"] = st.number_input("Month *", min_value=1, max_value=12, value=5)
                    payload["DayOfWeek"] = st.selectbox("Day of Week *", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                    payload["Day"] = st.number_input("Day of Month", min_value=1, max_value=31, value=15)

            elif table_name == "iucr_codes":
                payload["iucr"] = st.text_input("IUCR Code * (e.g. 999A)")
                payload["primary_type"] = st.text_input("Primary Type * (e.g. THEFT)")
                payload["description"] = st.text_input("Secondary Description *")
                payload["index_code"] = st.text_input("Index Code (I / N)")

            elif table_name == "city_community":
                payload["community_code"] = st.number_input("Community Code *", min_value=1, max_value=200, value=78)
                payload["community_name"] = st.text_input("Community Name *")
                payload["population"] = st.number_input("Population", min_value=0, value=25000)
                payload["area_sqmile"] = st.number_input("Area (Sq. Mile)", value=2.5)
                payload["area_sqkm"] = st.number_input("Area (Sq. Km)", value=6.4)
                payload["density_per_sqmi"] = st.number_input("Density per Sq. Mile", value=10000.0)
                payload["density_per_sqkm"] = st.number_input("Density per Sq. Km", value=3800.0)

            elif table_name == "district_ps_info":
                payload["district_code"] = st.number_input("District Code *", min_value=1, value=26)
                payload["district_name"] = st.text_input("District Name *", value="New District")
                payload["address"] = st.text_input("Address", value="100 W Madison St")
                payload["city"] = st.text_input("City", value="Chicago")
                payload["state"] = st.text_input("State", value="IL")
                payload["zip"] = st.number_input("Zip Code", value=60602)
                payload["phone"] = st.text_input("Phone", value="312-744-0000")

            elif table_name == "police_beat_info":
                payload["beat_num"] = st.number_input("Beat Number *", min_value=1, value=9999)
                payload["district"] = st.number_input("District", min_value=1, value=1)
                payload["sector"] = st.number_input("Sector", min_value=1, value=1)
                payload["beat"] = st.number_input("Beat", min_value=1, value=1)

            elif table_name == "ward_office":
                payload["ward"] = st.number_input("Ward Number *", min_value=1, value=51)
                payload["alderman"] = st.text_input("Alderman Name *", value="Jane Doe")
                payload["address"] = st.text_input("Office Address", value="123 Main St")
                payload["city"] = st.text_input("City", value="Chicago")
                payload["state"] = st.text_input("State", value="IL")
                payload["zipcode"] = st.number_input("Zip Code", value=60601)
                payload["ward_phone"] = st.text_input("Ward Phone", value="312-555-0100")
                payload["email"] = st.text_input("Email", value="alderman@cityofchicago.org")

            submit_add = st.form_submit_button("🚀 Submit & Create Record", use_container_width=True)
            if submit_add:
                try:
                    res = requests.post(f"{API_BASE_URL}/api/tables/{table_name}", json=payload)
                    if res.status_code == 201:
                        st.success(f"✅ Record successfully added to `{table_name}`!")
                        st.json(res.json().get("data", {}))
                    elif res.status_code == 409:
                        st.error(f"❌ Primary Key or Foreign Key conflict (409): {res.json().get('detail')}")
                    else:
                        st.error(f"❌ Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Failed to submit request: {e}")

    # --------------------------------------------------------------------------
    # TAB 3: MODIFY RECORD
    # --------------------------------------------------------------------------
    with tab_modify:
        st.markdown(f"### ✏️ Edit Existing Record in `{table_name}`")
        st.markdown(f"Enter the Primary Key (`{pk_name}`) to load current data into an editable form.")

        target_pk = st.text_input(f"Enter Target Record Primary Key (`{pk_name}`):", key=f"mod_pk_{table_name}")
        
        if st.button("🔍 Load Record for Editing", key=f"btn_load_{table_name}"):
            if not target_pk.strip():
                st.warning("Please enter a valid Primary Key value.")
            else:
                existing_record = fetch_api(f"/api/tables/{table_name}/{target_pk.strip()}")
                if existing_record:
                    st.session_state[f"edit_data_{table_name}"] = existing_record
                    st.session_state[f"edit_pk_{table_name}"] = target_pk.strip()

        # Render pre-filled edit form if record loaded
        if f"edit_data_{table_name}" in st.session_state:
            rec = st.session_state[f"edit_data_{table_name}"]
            loaded_pk = st.session_state[f"edit_pk_{table_name}"]
            st.info(f"Editing Record `{pk_name} = {loaded_pk}`")

            with st.form(f"form_edit_{table_name}"):
                update_payload = {}
                cols = list(rec.keys())

                for col in cols:
                    if col == pk_name:
                        st.text_input(f"{col} (Primary Key — Read Only)", value=str(rec[col]), disabled=True)
                    elif isinstance(rec[col], bool):
                        update_payload[col] = st.checkbox(col, value=bool(rec[col]))
                    elif isinstance(rec[col], int):
                        update_payload[col] = st.number_input(col, value=int(rec[col]))
                    elif isinstance(rec[col], float):
                        val = float(rec[col]) if not np.isnan(rec[col]) else 0.0
                        update_payload[col] = st.number_input(col, value=val, format="%.4f")
                    else:
                        val_str = str(rec[col]) if rec[col] is not None else ""
                        update_payload[col] = st.text_input(col, value=val_str)

                submit_modify = st.form_submit_button("💾 Save Changes", use_container_width=True)
                if submit_modify:
                    try:
                        res = requests.put(f"{API_BASE_URL}/api/tables/{table_name}/{loaded_pk}", json=update_payload)
                        if res.status_code == 200:
                            st.success(f"✅ Record `{loaded_pk}` updated successfully!")
                            st.json(res.json().get("data", {}))
                            del st.session_state[f"edit_data_{table_name}"]
                        else:
                            st.error(f"❌ Failed to update ({res.status_code}): {res.text}")
                    except Exception as e:
                        st.error(f"Update error: {e}")

    # --------------------------------------------------------------------------
    # TAB 4: DELETE RECORD
    # --------------------------------------------------------------------------
    with tab_delete:
        st.markdown(f"### 🗑️ Delete Record from `{table_name}`")
        st.markdown(f"Enter the Primary Key (`{pk_name}`) to preview the record before confirming deletion.")

        del_pk = st.text_input(f"Enter `{pk_name}` to Delete:", key=f"del_pk_{table_name}")
        
        if st.button("🔎 Locate Record to Delete", key=f"btn_find_del_{table_name}"):
            if not del_pk.strip():
                st.warning("Please enter a valid Primary Key value.")
            else:
                target_to_delete = fetch_api(f"/api/tables/{table_name}/{del_pk.strip()}")
                if target_to_delete:
                    st.session_state[f"target_del_{table_name}"] = target_to_delete
                    st.session_state[f"target_del_pk_{table_name}"] = del_pk.strip()

        # Confirmation card
        if f"target_del_{table_name}" in st.session_state:
            del_record = st.session_state[f"target_del_{table_name}"]
            cur_pk = st.session_state[f"target_del_pk_{table_name}"]
            
            st.warning(f"⚠️ **Attention:** You are about to permanently delete record `{pk_name} = {cur_pk}`.")
            st.json(del_record)

            c_del1, c_del2 = st.columns([1, 4])
            with c_del1:
                if st.button("🚨 Confirm Delete", type="primary", key=f"btn_confirm_del_{table_name}"):
                    try:
                        res = requests.delete(f"{API_BASE_URL}/api/tables/{table_name}/{cur_pk}")
                        if res.status_code == 200:
                            st.success(f"✅ Record `{cur_pk}` was deleted successfully from `{table_name}`.")
                            del st.session_state[f"target_del_{table_name}"]
                            del st.session_state[f"target_del_pk_{table_name}"]
                        elif res.status_code == 409:
                            st.error(f"❌ Cannot delete: Record is referenced by child tables as a Foreign Key.\n{res.json().get('detail')}")
                        else:
                            st.error(f"❌ Delete failed ({res.status_code}): {res.text}")
                    except Exception as e:
                        st.error(f"Error executing deletion: {e}")
            with c_del2:
                if st.button("Cancel", key=f"btn_cancel_del_{table_name}"):
                    del st.session_state[f"target_del_{table_name}"]
                    del st.session_state[f"target_del_pk_{table_name}"]
                    st.info("Deletion canceled.")
