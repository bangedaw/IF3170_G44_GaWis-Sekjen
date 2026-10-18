# Rekap Hasil Eksperimen

## Per konfigurasi

| experiment | label | algorithm | objective_name | runs | feasible_rate | final_objective_max | final_objective_mean | final_objective_std | final_value_mean | final_value_std | iterations_mean | iterations_std | duration_sec_mean | duration_sec_std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 1.00 | 5156.91 | 5087.22 | 62.29 | 3137.00 | 117.66 | 40.00 | 0.0000 | 0.2838 | 0.0091 |
|  | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 3 | 1.00 | 3242.00 | 3225.67 | 19.55 | 3225.67 | 19.55 | 40.00 | 0.0000 | 0.2749 | 0.0161 |
|  | random_restart_hc_multi_default | random_restart_hc | default | 3 | 1.00 | 3693.00 | 3634.33 | 53.27 | 3634.33 | 53.27 | 195.33 | 9.07 | 28.22 | 1.11 |
|  | sideways_move_hc_multi_default | sideways_move_hc | default | 3 | 1.00 | 3792.00 | 3709.33 | 72.15 | 3709.33 | 72.15 | 130.33 | 7.51 | 16.45 | 1.21 |
|  | simulated_annealing_multi_default | simulated_annealing | default | 3 | 1.00 | 3770.00 | 3681.67 | 76.70 | 3681.67 | 76.70 | 42582.00 | 0.0000 | 15.10 | 0.1631 |
|  | steepest_ascent_hc_multi_default | steepest_ascent_hc | default | 3 | 1.00 | 3486.00 | 3440.67 | 41.36 | 3440.67 | 41.36 | 18.67 | 1.53 | 2.73 | 0.2338 |
|  | stochastic_hc_multi_default | stochastic_hc | default | 3 | 1.00 | 3589.00 | 3438.67 | 130.54 | 3438.67 | 130.54 | 43.67 | 4.73 | 6.33 | 0.5832 |

## Per run

| experiment | file | label | algorithm | objective_name | seed | initial_objective | final_objective | final_value | feasible | iterations | duration_sec | restarts | max_restart | sideways_used | max_sideways | stuck_count | population_size | generations | value_per_truck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | ga_multi_alt_pop30_gen40_1.json | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 1 | 4341.28 | 5036.97 | 3144.00 | True | 40 | 0.2838 |  |  |  |  |  | 30 | 40 | [932.0, 611.0, 1601.0] |
|  | ga_multi_alt_pop30_gen40_2.json | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 2 | 4396.96 | 5067.79 | 3016.00 | True | 40 | 0.2747 |  |  |  |  |  | 30 | 40 | [670.0, 598.0, 1748.0] |
|  | ga_multi_alt_pop30_gen40_3.json | ga_multi_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 4407.84 | 5156.91 | 3251.00 | True | 40 | 0.2930 |  |  |  |  |  | 30 | 40 | [939.0, 517.0, 1795.0] |
|  | ga_multi_default_pop30_gen40_1.json | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 1 | 2689.00 | 3242.00 | 3242.00 | True | 40 | 0.2573 |  |  |  |  |  | 30 | 40 | [802.0, 678.0, 1762.0] |
|  | ga_multi_default_pop30_gen40_2.json | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 2 | 2640.00 | 3204.00 | 3204.00 | True | 40 | 0.2785 |  |  |  |  |  | 30 | 40 | [755.0, 551.0, 1898.0] |
|  | ga_multi_default_pop30_gen40_3.json | ga_multi_default_pop30_gen40 | genetic_algorithm | default | 3 | 2745.00 | 3231.00 | 3231.00 | True | 40 | 0.2889 |  |  |  |  |  | 30 | 40 | [980.0, 490.0, 1761.0] |
|  | random_restart_hc_multi_default_1.json | random_restart_hc_multi_default | random_restart_hc | default | 1 | 2170.00 | 3693.00 | 3693.00 | True | 185 | 27.01 | 10 | 10 |  |  |  |  |  | [1130.0, 551.0, 2012.0] |
|  | random_restart_hc_multi_default_2.json | random_restart_hc_multi_default | random_restart_hc | default | 2 | 1831.00 | 3589.00 | 3589.00 | True | 199 | 28.46 | 10 | 10 |  |  |  |  |  | [1030.0, 523.0, 2036.0] |
|  | random_restart_hc_multi_default_3.json | random_restart_hc_multi_default | random_restart_hc | default | 3 | 2029.00 | 3621.00 | 3621.00 | True | 202 | 29.18 | 10 | 10 |  |  |  |  |  | [986.0, 600.0, 2035.0] |
|  | sideways_move_hc_multi_default_1.json | sideways_move_hc_multi_default | sideways_move_hc | default | 1 | 2170.00 | 3677.00 | 3677.00 | True | 138 | 17.78 |  |  | 100 | 100 |  |  |  | [1020.0, 686.0, 1971.0] |
|  | sideways_move_hc_multi_default_2.json | sideways_move_hc_multi_default | sideways_move_hc | default | 2 | 1831.00 | 3792.00 | 3792.00 | True | 130 | 16.16 |  |  | 100 | 100 |  |  |  | [1119.0, 649.0, 2024.0] |
|  | sideways_move_hc_multi_default_3.json | sideways_move_hc_multi_default | sideways_move_hc | default | 3 | 2029.00 | 3659.00 | 3659.00 | True | 123 | 15.41 |  |  | 100 | 100 |  |  |  | [983.0, 662.0, 2014.0] |
|  | simulated_annealing_multi_default_1.json | simulated_annealing_multi_default | simulated_annealing | default | 1 | 2170.00 | 3643.00 | 3643.00 | True | 42582 | 15.08 |  |  |  |  | 68 |  |  | [1053.0, 636.0, 1954.0] |
|  | simulated_annealing_multi_default_2.json | simulated_annealing_multi_default | simulated_annealing | default | 2 | 1831.00 | 3632.00 | 3632.00 | True | 42582 | 15.27 |  |  |  |  | 67 |  |  | [1049.0, 659.0, 1924.0] |
|  | simulated_annealing_multi_default_3.json | simulated_annealing_multi_default | simulated_annealing | default | 3 | 2029.00 | 3770.00 | 3770.00 | True | 42582 | 14.95 |  |  |  |  | 64 |  |  | [995.0, 710.0, 2065.0] |
|  | steepest_ascent_hc_multi_default_1.json | steepest_ascent_hc_multi_default | steepest_ascent_hc | default | 1 | 2170.00 | 3431.00 | 3431.00 | True | 20 | 2.97 |  |  |  |  |  |  |  | [975.0, 603.0, 1853.0] |
|  | steepest_ascent_hc_multi_default_2.json | steepest_ascent_hc_multi_default | steepest_ascent_hc | default | 2 | 1831.00 | 3405.00 | 3405.00 | True | 19 | 2.72 |  |  |  |  |  |  |  | [1114.0, 609.0, 1682.0] |
|  | steepest_ascent_hc_multi_default_3.json | steepest_ascent_hc_multi_default | steepest_ascent_hc | default | 3 | 2029.00 | 3486.00 | 3486.00 | True | 17 | 2.50 |  |  |  |  |  |  |  | [1029.0, 591.0, 1866.0] |
|  | stochastic_hc_multi_default_1.json | stochastic_hc_multi_default | stochastic_hc | default | 1 | 2170.00 | 3373.00 | 3373.00 | True | 40 | 6.09 |  |  |  |  |  |  |  | [982.0, 606.0, 1785.0] |
|  | stochastic_hc_multi_default_2.json | stochastic_hc_multi_default | stochastic_hc | default | 2 | 1831.00 | 3354.00 | 3354.00 | True | 42 | 5.91 |  |  |  |  |  |  |  | [969.0, 553.0, 1832.0] |
|  | stochastic_hc_multi_default_3.json | stochastic_hc_multi_default | stochastic_hc | default | 3 | 2029.00 | 3589.00 | 3589.00 | True | 49 | 7.00 |  |  |  |  |  |  |  | [1035.0, 691.0, 1863.0] |
