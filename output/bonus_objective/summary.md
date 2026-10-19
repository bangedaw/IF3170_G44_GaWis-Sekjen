# Rekap Hasil Eksperimen

## Per konfigurasi

| experiment | label | algorithm | objective_name | runs | feasible_rate | final_objective_max | final_objective_mean | final_objective_std | final_value_mean | final_value_std | iterations_mean | iterations_std | duration_sec_mean | duration_sec_std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | first_choice_hc_alt | first_choice_hc | alt | 3 | 1.00 | 3765.94 | 3707.22 | 52.39 | 2217.33 | 58.01 | 32.67 | 4.51 | 0.1729 | 0.0432 |
|  | ga_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 1.00 | 3655.20 | 3585.97 | 62.76 | 2188.00 | 51.39 | 40.00 | 0.0000 | 0.1711 | 0.0045 |
|  | ga_default_pop30_gen40 | genetic_algorithm | default | 3 | 1.00 | 2159.00 | 2140.00 | 28.69 | 2140.00 | 28.69 | 40.00 | 0.0000 | 0.1690 | 0.0074 |
|  | random_restart_hc_alt | random_restart_hc | alt | 3 | 1.00 | 3811.44 | 3766.86 | 70.19 | 2267.33 | 49.80 | 132.00 | 7.55 | 7.30 | 0.3696 |
|  | sideways_move_hc_alt | sideways_move_hc | alt | 3 | 1.00 | 3952.54 | 3911.45 | 43.49 | 2352.00 | 53.56 | 121.00 | 1.00 | 6.52 | 0.1927 |
|  | simulated_annealing_alt | simulated_annealing | alt | 3 | 1.00 | 4101.58 | 4061.19 | 44.14 | 2470.00 | 53.93 | 42582.00 | 0.0000 | 14.51 | 0.4606 |
|  | steepest_ascent_hc_alt | steepest_ascent_hc | alt | 3 | 1.00 | 3685.95 | 3637.27 | 71.82 | 2175.67 | 39.46 | 15.00 | 1.00 | 0.8310 | 0.0195 |
|  | stochastic_hc_alt | stochastic_hc | alt | 3 | 1.00 | 3570.23 | 3493.55 | 73.77 | 2104.00 | 78.02 | 25.00 | 4.36 | 1.34 | 0.2848 |

## Per run

| experiment | file | label | algorithm | objective_name | seed | initial_objective | final_objective | final_value | feasible | iterations | duration_sec | restarts | max_restart | sideways_used | max_sideways | stuck_count | population_size | generations | value_per_truck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | first_choice_hc_alt_1.json | first_choice_hc_alt | first_choice_hc | alt | 1 | 1460.88 | 3765.94 | 2276.00 | True | 37 | 0.1465 |  |  |  |  |  |  |  | [2276.0] |
|  | first_choice_hc_alt_2.json | first_choice_hc_alt | first_choice_hc | alt | 2 | 1670.68 | 3665.26 | 2160.00 | True | 28 | 0.2227 |  |  |  |  |  |  |  | [2160.0] |
|  | first_choice_hc_alt_3.json | first_choice_hc_alt | first_choice_hc | alt | 3 | 1500.59 | 3690.46 | 2216.00 | True | 33 | 0.1494 |  |  |  |  |  |  |  | [2216.0] |
|  | ga_alt_pop30_gen40_1.json | ga_alt_pop30_gen40 | genetic_algorithm | alt | 1 | 2937.18 | 3532.81 | 2132.00 | True | 40 | 0.1698 |  |  |  |  |  | 30 | 40 | [2132.0] |
|  | ga_alt_pop30_gen40_2.json | ga_alt_pop30_gen40 | genetic_algorithm | alt | 2 | 3233.97 | 3655.20 | 2233.00 | True | 40 | 0.1675 |  |  |  |  |  | 30 | 40 | [2233.0] |
|  | ga_alt_pop30_gen40_3.json | ga_alt_pop30_gen40 | genetic_algorithm | alt | 3 | 3046.00 | 3569.88 | 2199.00 | True | 40 | 0.1761 |  |  |  |  |  | 30 | 40 | [2199.0] |
|  | ga_default_pop30_gen40_1.json | ga_default_pop30_gen40 | genetic_algorithm | default | 1 | 1835.00 | 2107.00 | 2107.00 | True | 40 | 0.1678 |  |  |  |  |  | 30 | 40 | [2107.0] |
|  | ga_default_pop30_gen40_2.json | ga_default_pop30_gen40 | genetic_algorithm | default | 2 | 1964.00 | 2154.00 | 2154.00 | True | 40 | 0.1623 |  |  |  |  |  | 30 | 40 | [2154.0] |
|  | ga_default_pop30_gen40_3.json | ga_default_pop30_gen40 | genetic_algorithm | default | 3 | 1819.00 | 2159.00 | 2159.00 | True | 40 | 0.1770 |  |  |  |  |  | 30 | 40 | [2159.0] |
|  | random_restart_hc_alt_1.json | random_restart_hc_alt | random_restart_hc | alt | 1 | 1460.88 | 3803.18 | 2320.00 | True | 140 | 7.72 | 10 | 10 |  |  |  |  |  | [2320.0] |
|  | random_restart_hc_alt_2.json | random_restart_hc_alt | random_restart_hc | alt | 2 | 1670.68 | 3811.44 | 2261.00 | True | 125 | 7.03 | 10 | 10 |  |  |  |  |  | [2261.0] |
|  | random_restart_hc_alt_3.json | random_restart_hc_alt | random_restart_hc | alt | 3 | 1500.59 | 3685.95 | 2221.00 | True | 131 | 7.15 | 10 | 10 |  |  |  |  |  | [2221.0] |
|  | sideways_move_hc_alt_1.json | sideways_move_hc_alt | sideways_move_hc | alt | 1 | 1460.88 | 3865.91 | 2369.00 | True | 122 | 6.74 |  |  | 100 | 100 |  |  |  | [2369.0] |
|  | sideways_move_hc_alt_2.json | sideways_move_hc_alt | sideways_move_hc | alt | 2 | 1670.68 | 3915.89 | 2292.00 | True | 121 | 6.38 |  |  | 100 | 100 |  |  |  | [2292.0] |
|  | sideways_move_hc_alt_3.json | sideways_move_hc_alt | sideways_move_hc | alt | 3 | 1500.59 | 3952.54 | 2395.00 | True | 120 | 6.43 |  |  | 100 | 100 |  |  |  | [2395.0] |
|  | simulated_annealing_alt_1.json | simulated_annealing_alt | simulated_annealing | alt | 1 | 1460.88 | 4014.07 | 2434.00 | True | 42582 | 14.27 |  |  |  |  | 74 |  |  | [2434.0] |
|  | simulated_annealing_alt_2.json | simulated_annealing_alt | simulated_annealing | alt | 2 | 1670.68 | 4101.58 | 2532.00 | True | 42582 | 15.04 |  |  |  |  | 77 |  |  | [2532.0] |
|  | simulated_annealing_alt_3.json | simulated_annealing_alt | simulated_annealing | alt | 3 | 1500.59 | 4067.92 | 2444.00 | True | 42582 | 14.22 |  |  |  |  | 71 |  |  | [2444.0] |
|  | steepest_ascent_hc_alt_1.json | steepest_ascent_hc_alt | steepest_ascent_hc | alt | 1 | 1460.88 | 3554.79 | 2149.00 | True | 14 | 0.8455 |  |  |  |  |  |  |  | [2149.0] |
|  | steepest_ascent_hc_alt_2.json | steepest_ascent_hc_alt | steepest_ascent_hc | alt | 2 | 1670.68 | 3671.07 | 2157.00 | True | 15 | 0.8088 |  |  |  |  |  |  |  | [2157.0] |
|  | steepest_ascent_hc_alt_3.json | steepest_ascent_hc_alt | steepest_ascent_hc | alt | 3 | 1500.59 | 3685.95 | 2221.00 | True | 16 | 0.8385 |  |  |  |  |  |  |  | [2221.0] |
|  | stochastic_hc_alt_1.json | stochastic_hc_alt | stochastic_hc | alt | 1 | 1460.88 | 3570.23 | 2183.00 | True | 30 | 1.67 |  |  |  |  |  |  |  | [2183.0] |
|  | stochastic_hc_alt_2.json | stochastic_hc_alt | stochastic_hc | alt | 2 | 1670.68 | 3423.09 | 2027.00 | True | 22 | 1.13 |  |  |  |  |  |  |  | [2027.0] |
|  | stochastic_hc_alt_3.json | stochastic_hc_alt | stochastic_hc | alt | 3 | 1500.59 | 3487.34 | 2102.00 | True | 23 | 1.22 |  |  |  |  |  |  |  | [2102.0] |
