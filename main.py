import streamlit as st
import datetime as dt

from config import SCHEMES
from queries import SIMULATION_QUERY
from db import fetch_dataframe

# PAGE CONFIG
st.set_page_config(
    page_title="Simulasi Penggajian – Branch Bekasi",
    layout="wide"
)

st.title("Simulasi Penggajian – Branch Bekasi")

# SIDEBAR FILTER
branch = "Jakarta"

st.sidebar.header("Filter Simulasi")

scheme_name = st.sidebar.selectbox(
    "Skema Penggajian",
    SCHEMES.keys()
)

use_perbantuan = st.sidebar.checkbox(
    "Gunakan Perbantuan",
    value=False
)

days = st.sidebar.slider(
    "Jumlah Hari",
    min_value=1,
    max_value=30,
    value=30
)

start_date = dt.date(2025, 11, 1)
end_date = start_date + dt.timedelta(days=days - 1)

scheme = SCHEMES[scheme_name]
bonus_amount = scheme["max_salary"] - scheme["gapok"]

# SCHEME SUMMARY
st.subheader(f"Ringkasan Skema – {scheme_name}")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Gapok / Hari", f"Rp {scheme['gapok']:,}")
col2.metric("Bonus Maksimal", f"Rp {bonus_amount:,}")
col3.metric("Target Sales Bonus", f"Rp {scheme['bonus_threshold']:,}")
col4.metric("Max Salary / Hari", f"Rp {scheme['max_salary']:,}")
col5.metric("Periode Simulasi", f"{days} Hari")

# LOAD DATA
params = {
    "branch": branch,
    "start_date": start_date,
    "end_date": end_date,
    "gapok": scheme["gapok"],
    "max_salary": scheme["max_salary"],
    "bonus_threshold": scheme["bonus_threshold"],
    "use_perbantuan": use_perbantuan
}

df = fetch_dataframe(SIMULATION_QUERY, params)

if df.empty:
    st.warning("Data kosong untuk filter yang dipilih")
    st.stop()

# RANGE TOTAL SALARY
st.subheader("Range Total Salary")

min_total_salary = scheme["gapok"] * days
max_total_salary = scheme["max_salary"] * days

col1, col2 = st.columns(2)

col1.metric(
    "Minimum",
    f"Rp {min_total_salary:,.0f}",
    help="Gapok × jumlah hari (tanpa bonus)"
)

col2.metric(
    "Maksimum",
    f"Rp {max_total_salary:,.0f}",
    help="Max salary × jumlah hari (semua hari dapat bonus)"
)

# BONUS DISTRIBUTION
st.subheader("Distribusi Bonus")

bonus_dist = (
    df.groupby("keterangan_bonus")
      .size()
      .reset_index(name="jumlah_data")
)

bonus_dist["persentase"] = (
    bonus_dist["jumlah_data"] / bonus_dist["jumlah_data"].sum()
).round(3)

st.dataframe(
    bonus_dist,
    use_container_width=True
)

# TOTAL SUMMARY
st.subheader("Ringkasan Total")

total_sales = df["sales"].sum()
total_no_os = df["total_salary_no_os"].sum()
total_os_8 = df["total_salary_os_8"].sum()
total_os_10 = df["total_salary_os_10"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"Rp {total_sales:,.0f}")
col2.metric("Total Salary (Tanpa OS)", f"Rp {total_no_os:,.0f}")
col3.metric("Total Salary (OS 8%)", f"Rp {total_os_8:,.0f}")
col4.metric("Total Salary (OS 10%)", f"Rp {total_os_10:,.0f}")

# SALARY COST PERCENTAGE
st.subheader("Salary Cost")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Tanpa OS",
    f"{total_no_os / total_sales:.2%}"
)

col2.metric(
    "Dengan OS 8%",
    f"{total_os_8 / total_sales:.2%}"
)

col3.metric(
    "Dengan OS 10%",
    f"{total_os_10 / total_sales:.2%}"
)

# DETAIL TABLE
with st.expander("Detail Harian", expanded=False):
    st.dataframe(
        df.sort_values(["tanggal", "outlet"]),
        use_container_width=True
    )
