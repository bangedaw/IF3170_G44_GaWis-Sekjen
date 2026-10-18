# Rekap Hasil Eksperimen

## Per konfigurasi

| experiment | label | algorithm | objective_name | runs | feasible_rate | final_objective_max | final_objective_mean | final_objective_std | final_value_mean | final_value_std | iterations_mean | iterations_std | duration_sec_mean | duration_sec_std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_ctrl_gen40_pop15 | genetic_algorithm | default | 3 | 1.00 | 2062.00 | 1950.00 | 111.01 | 1950.00 | 111.01 | 40.00 | 0.0000 | 0.1568 | 0.0089 |
|  | ga_ctrl_gen40_pop30 | genetic_algorithm | default | 3 | 1.00 | 2159.00 | 2140.00 | 28.69 | 2140.00 | 28.69 | 40.00 | 0.0000 | 0.3268 | 0.0073 |
|  | ga_ctrl_gen40_pop60 | genetic_algorithm | default | 3 | 1.00 | 2295.00 | 2234.00 | 60.02 | 2234.00 | 60.02 | 40.00 | 0.0000 | 0.7248 | 0.1007 |
|  | ga_ctrl_pop30_gen20 | genetic_algorithm | default | 3 | 1.00 | 2159.00 | 2097.67 | 66.49 | 2097.67 | 66.49 | 20.00 | 0.0000 | 0.2764 | 0.0238 |
|  | ga_ctrl_pop30_gen40 | genetic_algorithm | default | 3 | 1.00 | 2159.00 | 2140.00 | 28.69 | 2140.00 | 28.69 | 40.00 | 0.0000 | 0.3916 | 0.0817 |
|  | ga_ctrl_pop30_gen60 | genetic_algorithm | default | 3 | 1.00 | 2227.00 | 2182.33 | 65.62 | 2182.33 | 65.62 | 60.00 | 0.0000 | 0.6700 | 0.0579 |

## Per run

| experiment | file | label | algorithm | objective_name | seed | initial_objective | final_objective | final_value | feasible | iterations | duration_sec | restarts | max_restart | sideways_used | max_sideways | stuck_count | population_size | generations | value_per_truck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_ctrl_gen40_pop15_1.json | ga_ctrl_gen40_pop15 | genetic_algorithm | default | 1 | 1654.00 | 1840.00 | 1840.00 | True | 40 | 0.1475 |  |  |  |  |  | 15 | 40 | [1840.0] |
|  | ga_ctrl_gen40_pop15_2.json | ga_ctrl_gen40_pop15 | genetic_algorithm | default | 2 | 1751.00 | 1948.00 | 1948.00 | True | 40 | 0.1651 |  |  |  |  |  | 15 | 40 | [1948.0] |
|  | ga_ctrl_gen40_pop15_3.json | ga_ctrl_gen40_pop15 | genetic_algorithm | default | 3 | 1693.00 | 2062.00 | 2062.00 | True | 40 | 0.1578 |  |  |  |  |  | 15 | 40 | [2062.0] |
|  | ga_ctrl_gen40_pop30_1.json | ga_ctrl_gen40_pop30 | genetic_algorithm | default | 1 | 1835.00 | 2107.00 | 2107.00 | True | 40 | 0.3350 |  |  |  |  |  | 30 | 40 | [2107.0] |
|  | ga_ctrl_gen40_pop30_2.json | ga_ctrl_gen40_pop30 | genetic_algorithm | default | 2 | 1964.00 | 2154.00 | 2154.00 | True | 40 | 0.3210 |  |  |  |  |  | 30 | 40 | [2154.0] |
|  | ga_ctrl_gen40_pop30_3.json | ga_ctrl_gen40_pop30 | genetic_algorithm | default | 3 | 1819.00 | 2159.00 | 2159.00 | True | 40 | 0.3243 |  |  |  |  |  | 30 | 40 | [2159.0] |
|  | ga_ctrl_gen40_pop60_1.json | ga_ctrl_gen40_pop60 | genetic_algorithm | default | 1 | 1835.00 | 2175.00 | 2175.00 | True | 40 | 0.6384 |  |  |  |  |  | 60 | 40 | [2175.0] |
|  | ga_ctrl_gen40_pop60_2.json | ga_ctrl_gen40_pop60 | genetic_algorithm | default | 2 | 1964.00 | 2295.00 | 2295.00 | True | 40 | 0.7006 |  |  |  |  |  | 60 | 40 | [2295.0] |
|  | ga_ctrl_gen40_pop60_3.json | ga_ctrl_gen40_pop60 | genetic_algorithm | default | 3 | 1819.00 | 2232.00 | 2232.00 | True | 40 | 0.8355 |  |  |  |  |  | 60 | 40 | [2232.0] |
|  | ga_ctrl_pop30_gen20_1.json | ga_ctrl_pop30_gen20 | genetic_algorithm | default | 1 | 1835.00 | 2107.00 | 2107.00 | True | 20 | 0.2992 |  |  |  |  |  | 30 | 20 | [2107.0] |
|  | ga_ctrl_pop30_gen20_2.json | ga_ctrl_pop30_gen20 | genetic_algorithm | default | 2 | 1964.00 | 2027.00 | 2027.00 | True | 20 | 0.2784 |  |  |  |  |  | 30 | 20 | [2027.0] |
|  | ga_ctrl_pop30_gen20_3.json | ga_ctrl_pop30_gen20 | genetic_algorithm | default | 3 | 1819.00 | 2159.00 | 2159.00 | True | 20 | 0.2516 |  |  |  |  |  | 30 | 20 | [2159.0] |
|  | ga_ctrl_pop30_gen40_1.json | ga_ctrl_pop30_gen40 | genetic_algorithm | default | 1 | 1835.00 | 2107.00 | 2107.00 | True | 40 | 0.4860 |  |  |  |  |  | 30 | 40 | [2107.0] |
|  | ga_ctrl_pop30_gen40_2.json | ga_ctrl_pop30_gen40 | genetic_algorithm | default | 2 | 1964.00 | 2154.00 | 2154.00 | True | 40 | 0.3467 |  |  |  |  |  | 30 | 40 | [2154.0] |
|  | ga_ctrl_pop30_gen40_3.json | ga_ctrl_pop30_gen40 | genetic_algorithm | default | 3 | 1819.00 | 2159.00 | 2159.00 | True | 40 | 0.3422 |  |  |  |  |  | 30 | 40 | [2159.0] |
|  | ga_ctrl_pop30_gen60_1.json | ga_ctrl_pop30_gen60 | genetic_algorithm | default | 1 | 1835.00 | 2107.00 | 2107.00 | True | 60 | 0.6544 |  |  |  |  |  | 30 | 60 | [2107.0] |
|  | ga_ctrl_pop30_gen60_2.json | ga_ctrl_pop30_gen60 | genetic_algorithm | default | 2 | 1964.00 | 2227.00 | 2227.00 | True | 60 | 0.6216 |  |  |  |  |  | 30 | 60 | [2227.0] |
|  | ga_ctrl_pop30_gen60_3.json | ga_ctrl_pop30_gen60 | genetic_algorithm | default | 3 | 1819.00 | 2213.00 | 2213.00 | True | 60 | 0.7342 |  |  |  |  |  | 30 | 60 | [2213.0] |
