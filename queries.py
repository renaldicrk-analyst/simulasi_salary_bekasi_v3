# queries.py

SIMULATION_QUERY = """
WITH base AS (
    SELECT
        tanggal,
        outlet,
        branch,
        sales
    FROM mv_manpower_cost_v2
    WHERE branch = %(branch)s
      AND tanggal BETWEEN %(start_date)s AND %(end_date)s
      AND manpower_optimal = 1
),

salary_logic AS (
    SELECT
        tanggal,
        outlet,
        sales,

        CASE
            WHEN sales >= %(bonus_threshold)s THEN 'DAPAT BONUS'
            ELSE 'TIDAK DAPAT BONUS'
        END AS keterangan_bonus,

        CASE
            WHEN sales >= %(bonus_threshold)s THEN %(max_salary)s
            ELSE %(gapok)s
        END AS gaji_crew_utama
    FROM base
),

crew_logic AS (
    SELECT
        *,
        CASE
            WHEN %(use_perbantuan)s = false THEN 0
            WHEN sales > 3500000 THEN 3
            WHEN sales > 2500000 THEN 2
            WHEN sales > 1500000 THEN 1
            ELSE 0
        END AS crew_perbantuan,
        90000 AS gaji_perbantuan
    FROM salary_logic
)

SELECT
    tanggal,
    outlet,
    sales,
    keterangan_bonus,

    gaji_crew_utama,
    crew_perbantuan,
    crew_perbantuan * gaji_perbantuan AS total_gaji_perbantuan,

    gaji_crew_utama + (crew_perbantuan * gaji_perbantuan) AS total_salary_no_os,
    (gaji_crew_utama * 1.08) + (crew_perbantuan * gaji_perbantuan) AS total_salary_os_8,
    (gaji_crew_utama * 1.10) + (crew_perbantuan * gaji_perbantuan) AS total_salary_os_10
FROM crew_logic
ORDER BY tanggal, outlet;
"""
