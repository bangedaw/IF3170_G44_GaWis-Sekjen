# Rekap Hasil Eksperimen

## Per konfigurasi

| experiment | label | algorithm | objective_name | runs | feasible_rate | final_objective_max | final_objective_mean | final_objective_std | final_value_mean | final_value_std | iterations_mean | iterations_std | duration_sec_mean | duration_sec_std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 1.00 | 5156.91 | 5087.22 | 62.29 | 3137.00 | 117.66 | 40.00 | 0.0000 | 0.2838 | 0.0091 |
|  | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 3 | 1.00 | 3242.00 | 3225.67 | 19.55 | 3225.67 | 19.55 | 40.00 | 0.0000 | 0.2749 | 0.0161 |

## Per run

| experiment | file | label | algorithm | objective_name | seed | initial_objective | final_objective | final_value | feasible | iterations | duration_sec | restarts | max_restart | sideways_used | max_sideways | stuck_count | population_size | generations | value_per_truck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_multi_alt_pop30_gen40_1.json | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 1 | 4341.28 | 5036.97 | 3144.00 | True | 40 | 0.2838 |  |  |  |  |  | 30 | 40 | [932.0, 611.0, 1601.0] |
|  | ga_multi_alt_pop30_gen40_2.json | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 2 | 4396.96 | 5067.79 | 3016.00 | True | 40 | 0.2747 |  |  |  |  |  | 30 | 40 | [670.0, 598.0, 1748.0] |
|  | ga_multi_alt_pop30_gen40_3.json | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 4407.84 | 5156.91 | 3251.00 | True | 40 | 0.2930 |  |  |  |  |  | 30 | 40 | [939.0, 517.0, 1795.0] |
|  | ga_multi_default_pop30_gen40_1.json | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 1 | 2689.00 | 3242.00 | 3242.00 | True | 40 | 0.2573 |  |  |  |  |  | 30 | 40 | [802.0, 678.0, 1762.0] |
|  | ga_multi_default_pop30_gen40_2.json | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 2 | 2640.00 | 3204.00 | 3204.00 | True | 40 | 0.2785 |  |  |  |  |  | 30 | 40 | [755.0, 551.0, 1898.0] |
|  | ga_multi_default_pop30_gen40_3.json | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 3 | 2745.00 | 3231.00 | 3231.00 | True | 40 | 0.2889 |  |  |  |  |  | 30 | 40 | [980.0, 490.0, 1761.0] |
