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
-- LOGIKA BONUS HARIAN BERJENJANG (HANYA HARI ≥ THRESHOLD)
-- ======================================================
bonus_logic AS (
    SELECT
        *,
        CASE
            WHEN sales >= %(daily_bonus_threshold)s AND sales >= %(tier_3_sales)s THEN sales * %(tier_3_pct)s
            WHEN sales >= %(daily_bonus_threshold)s AND sales >= %(tier_2_sales)s THEN sales * %(tier_2_pct)s
            WHEN sales >= %(daily_bonus_threshold)s AND sales >= %(tier_1_sales)s THEN sales * %(tier_1_pct)s
            ELSE 0
        END AS bonus_crew_utama
    FROM base
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