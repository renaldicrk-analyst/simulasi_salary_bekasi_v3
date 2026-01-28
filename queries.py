CUSTOM6_QUERY = """
WITH base AS (
    SELECT
        tanggal,
        outlet,
        branch,
        sales
    FROM mv_manpower_cost_v2
    WHERE branch = %(branch)s
      AND tanggal BETWEEN %(start_date)s AND %(end_date)s
),

-- ======================================================
-- HITUNG TOTAL SALES BULANAN PER OUTLET
-- ======================================================
monthly_sales AS (
    SELECT
        outlet,
        SUM(sales) AS total_sales_bulanan
    FROM base
    GROUP BY outlet
),

-- ======================================================
-- TENTUKAN TIER BONUS BULANAN PER OUTLET
-- ======================================================
tier AS (
    SELECT
        m.outlet,
        m.total_sales_bulanan,
        CASE
            WHEN m.total_sales_bulanan >= %(tier_3_sales)s THEN %(tier_3_pct)s
            WHEN m.total_sales_bulanan >= %(tier_2_sales)s THEN %(tier_2_pct)s
            WHEN m.total_sales_bulanan >= %(tier_1_sales)s THEN %(tier_1_pct)s
            ELSE 0
        END AS bonus_pct
    FROM monthly_sales m
),

-- ======================================================
-- HITUNG BONUS HARIAN (HANYA HARI ≥ THRESHOLD)
-- ======================================================
bonus_logic AS (
    SELECT
        b.*,
        t.bonus_pct,
        CASE
            WHEN b.sales >= %(daily_bonus_threshold)s THEN b.sales * t.bonus_pct
            ELSE 0
        END AS bonus_crew_utama
    FROM base b
    LEFT JOIN tier t ON b.outlet = t.outlet
),

-- ======================================================
-- LOGIKA CREW PERBANTUAN
-- ======================================================
crew_logic AS (
    SELECT
        *,
        CASE
            WHEN %(use_perbantuan)s = 0 THEN 0
            WHEN sales >= %(crew_3_threshold)s THEN 3
            WHEN sales >= %(crew_2_threshold)s THEN 2
            WHEN sales >= %(crew_1_threshold)s THEN 1
            ELSE 0
        END AS crew_perbantuan,
        %(gaji_perbantuan)s AS gaji_perbantuan,
        %(gapok)s AS gapok
    FROM bonus_logic
)

-- ======================================================
-- OUTPUT FINAL
-- ======================================================
SELECT
    tanggal,
    outlet,
    sales,
    gapok,
    crew_perbantuan,
    crew_perbantuan * gaji_perbantuan AS total_gaji_perbantuan,
    bonus_crew_utama,
    gapok + (crew_perbantuan * gaji_perbantuan) + bonus_crew_utama AS total_salary
FROM crew_logic
ORDER BY tanggal, outlet;
"""