# Rekap Hasil Eksperimen

## Per konfigurasi

| experiment | label | algorithm | objective_name | runs | feasible_rate | final_objective_max | final_objective_mean | final_objective_std | final_value_mean | final_value_std | iterations_mean | iterations_std | duration_sec_mean | duration_sec_std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 1.00 | 3655.20 | 3585.97 | 62.76 | 2188.00 | 51.39 | 40.00 | 0.0000 | 0.1711 | 0.0045 |
|  | ga_default_pop30_gen40 | genetic_algorithm | default | 3 | 1.00 | 2159.00 | 2140.00 | 28.69 | 2140.00 | 28.69 | 40.00 | 0.0000 | 0.1690 | 0.0074 |

## Per run

| experiment | file | label | algorithm | objective_name | seed | initial_objective | final_objective | final_value | feasible | iterations | duration_sec | restarts | max_restart | sideways_used | max_sideways | stuck_count | population_size | generations | value_per_truck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_alt_pop30_gen40_1.json | ga_alt_pop30_gen40 | genetic_algorithm | alt | 1 | 2937.18 | 3532.81 | 2132.00 | True | 40 | 0.1698 |  |  |  |  |  | 30 | 40 | [2132.0] |
|  | ga_alt_pop30_gen40_2.json | ga_alt_pop30_gen40 | genetic_algorithm | alt | 2 | 3233.97 | 3655.20 | 2233.00 | True | 40 | 0.1675 |  |  |  |  |  | 30 | 40 | [2233.0] |
|  | ga_alt_pop30_gen40_3.json | ga_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 3046.00 | 3569.88 | 2199.00 | True | 40 | 0.1761 |  |  |  |  |  | 30 | 40 | [2199.0] |
|  | ga_default_pop30_gen40_1.json | ga_default_pop30_gen40 | genetic_algorithm | default | 1 | 1835.00 | 2107.00 | 2107.00 | True | 40 | 0.1678 |  |  |  |  |  | 30 | 40 | [2107.0] |
|  | ga_default_pop30_gen40_2.json | ga_default_pop30_gen40 | genetic_algorithm | default | 2 | 1964.00 | 2154.00 | 2154.00 | True | 40 | 0.1623 |  |  |  |  |  | 30 | 40 | [2154.0] |
|  | ga_default_pop30_gen40_3.json | ga_default_pop30_gen40 | genetic_algorithm | default | 3 | 1819.00 | 2159.00 | 2159.00 | True | 40 | 0.1770 |  |  |  |  |  | 30 | 40 | [2159.0] |
