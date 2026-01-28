import streamlit as st
import datetime as dt
import pandas as pd

from queries import CUSTOM6_QUERY
from db import fetch_dataframe

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Simulasi Penggajian – Custom 6",
    layout="wide"
)

st.title("Simulasi Penggajian – Custom 6")

branch = "Jakarta"

# ======================================================
# SIDEBAR – PARAMETER SKEMA BARU
# ======================================================
st.sidebar.header("Skema Custom 6 – Bonus Bulanan Berjenjang (Sales Bulanan)")

# Jumlah hari kerja
days = st.sidebar.slider("Jumlah Hari Kerja", 1, 31, 26)
start_date = dt.date(2026, 1, 1)
end_date = start_date + dt.timedelta(days=days - 1)

# Gapok dan gaji perbantuan
gapok = st.sidebar.number_input("Gapok / Hari", value=115_000, step=5_000)
gaji_perbantuan = st.sidebar.number_input("Gaji Crew Perbantuan / Hari", value=100_000, step=5_000)

# ======================================================
# Jenjang bonus bulanan berdasarkan total sales
# ======================================================
st.sidebar.header("Tier Bonus Bulanan (Total Sales Outlet)")

tier_1_sales = st.sidebar.number_input("Tier 1 Total Sales Bulanan ≥", value=30_000_000)
tier_1_pct = st.sidebar.number_input("Bonus % Tier 1", value=0.05, step=0.005)

tier_2_sales = st.sidebar.number_input("Tier 2 Total Sales Bulanan ≥", value=51_000_000)
tier_2_pct = st.sidebar.number_input("Bonus % Tier 2", value=0.08, step=0.005)

tier_3_sales = st.sidebar.number_input("Tier 3 Total Sales Bulanan ≥", value=66_000_000)
tier_3_pct = st.sidebar.number_input("Bonus % Tier 3", value=0.10, step=0.005)

# ======================================================
# Threshold harian per tier
# ======================================================
st.sidebar.header("Threshold Harian per Tier")

daily_threshold_1 = st.sidebar.number_input("Sales minimal masuk bonus / hari – Tier 1", value=1_000_000, step=50_000)
daily_threshold_2 = st.sidebar.number_input("Sales minimal masuk bonus / hari – Tier 2", value=1_700_000, step=50_000)
daily_threshold_3 = st.sidebar.number_input("Sales minimal masuk bonus / hari – Tier 3", value=2_200_000, step=50_000)

# ======================================================
# Crew perbantuan
# ======================================================
st.sidebar.header("Crew Perbantuan")

use_perbantuan = st.sidebar.checkbox("Gunakan Crew Perbantuan", value=True)
crew_1_threshold = st.sidebar.number_input("Sales ≥ +1 Crew", value=1_700_000)
crew_2_threshold = st.sidebar.number_input("Sales ≥ +2 Crew", value=2_700_000)
crew_3_threshold = st.sidebar.number_input("Sales ≥ +3 Crew", value=3_700_000)

# ======================================================
# DESKRIPSI SKEMA
# ======================================================
st.info(
    f"""
**Skema Custom 6 – Bonus Bulanan berdasarkan Total Sales Bulanan**
- Gapok harian: Rp {gapok:,.0f}
- Bonus dihitung dari hari-hari yang lolos threshold harian sesuai tier
- Threshold harian per tier:
    - Tier 1: Rp {daily_threshold_1:,.0f}
    - Tier 2: Rp {daily_threshold_2:,.0f}
    - Tier 3: Rp {daily_threshold_3:,.0f}
- Jenjang bonus bulanan berdasarkan total sales outlet:
    - Tier 1 ≥ Rp {tier_1_sales:,.0f} → {tier_1_pct:.0%}
    - Tier 2 ≥ Rp {tier_2_sales:,.0f} → {tier_2_pct:.0%}
    - Tier 3 ≥ Rp {tier_3_sales:,.0f} → {tier_3_pct:.0%}
- Bonus dibayarkan di akhir bulan (total dari semua hari lolos threshold)
- Crew perbantuan: {"Aktif" if use_perbantuan else "Tidak digunakan"}
"""
)

# ======================================================
# PARAMETER SQL
# ======================================================
params = {
    "branch": branch,
    "start_date": start_date,
    "end_date": end_date,
    "gapok": gapok,
    "gaji_perbantuan": gaji_perbantuan,
    "tier_1_sales": tier_1_sales,
    "tier_2_sales": tier_2_sales,
    "tier_3_sales": tier_3_sales,
    "tier_1_pct": tier_1_pct,
    "tier_2_pct": tier_2_pct,
    "tier_3_pct": tier_3_pct,
    "daily_threshold_1": daily_threshold_1,
    "daily_threshold_2": daily_threshold_2,
    "daily_threshold_3": daily_threshold_3,
    "use_perbantuan": 1 if use_perbantuan else 0,
    "crew_1_threshold": crew_1_threshold,
    "crew_2_threshold": crew_2_threshold,
    "crew_3_threshold": crew_3_threshold,
}

# ======================================================
# LOAD DATA
# ======================================================
df = fetch_dataframe(CUSTOM6_QUERY, params)

if df.empty:
    st.warning("Data kosong")
    st.stop()

# ======================================================
# RINGKASAN BONUS & SALARY
# ======================================================
st.subheader("Ringkasan Bulanan")

bonus_df = df.groupby("outlet").agg(
    total_sales=("sales", "sum"),
    total_bonus=("bonus_crew_utama", "sum")
).reset_index()

total_sales = df["sales"].sum()
total_bonus = df["bonus_crew_utama"].sum()
total_salary = df["gapok"].sum() + df["total_gaji_perbantuan"].sum() + total_bonus

c1, c2, c3 = st.columns(3)
c1.metric("Total Sales", f"Rp {total_sales:,.0f}")
c2.metric("Total Bonus Bulanan", f"Rp {total_bonus:,.0f}")
c3.metric("Total Salary", f"Rp {total_salary:,.0f}")

st.metric("Salary Cost", f"{total_salary / total_sales:.2%}")

# ======================================================
# DETAIL HARIAN
# ======================================================
st.subheader("Detail Harian")
st.dataframe(
    df[
        [
            "tanggal",
            "outlet",
            "sales",
            "gapok",
            "crew_perbantuan",
            "total_gaji_perbantuan",
            "bonus_crew_utama",
            "total_salary",
        ]
    ],
    use_container_width=True
)