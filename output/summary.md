# Rekap Hasil Eksperimen

## Per konfigurasi

| experiment | label | algorithm | objective_name | runs | feasible_rate | final_objective_max | final_objective_mean | final_objective_std | final_value_mean | final_value_std | iterations_mean | iterations_std | duration_sec_mean | duration_sec_std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hill_climbing | random_restart_hc | random_restart_hc | default | 3 | 1.00 | 2462.00 | 2365.67 | 85.91 | 2365.67 | 85.91 | 138.00 | 6.93 | 10.50 | 0.2524 |
| hill_climbing | sideways_move_hc | sideways_move_hc | default | 3 | 1.00 | 2406.00 | 2395.00 | 16.52 | 2395.00 | 16.52 | 121.00 | 3.61 | 8.80 | 0.3570 |
| hill_climbing | steepest_ascent_hc | steepest_ascent_hc | default | 3 | 1.00 | 2279.00 | 2262.33 | 18.15 | 2262.33 | 18.15 | 16.00 | 2.00 | 1.21 | 0.1576 |
| hill_climbing | stochastic_hc | stochastic_hc | default | 3 | 1.00 | 2283.00 | 2192.67 | 81.13 | 2192.67 | 81.13 | 27.00 | 2.00 | 1.99 | 0.1179 |
| simulated_annealing | simulated_annealing | simulated_annealing | default | 3 | 1.00 | 2615.00 | 2604.67 | 17.90 | 2604.67 | 17.90 | 42582.00 | 0.0000 | 19.50 | 0.7301 |

## Per run

| experiment | file | label | algorithm | objective_name | seed | initial_objective | final_objective | final_value | feasible | iterations | duration_sec | restarts | max_restart | sideways_used | max_sideways | stuck_count | population_size | generations | value_per_truck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hill_climbing | hill_climbing/random_restart_hc_1.json | random_restart_hc | random_restart_hc | default | 1 | 879.00 | 2297.00 | 2297.00 | True | 134 | 10.45 | 10 | 10 |  |  |  |  |  | [2297.0] |
| hill_climbing | hill_climbing/random_restart_hc_2.json | random_restart_hc | random_restart_hc | default | 2 | 1107.00 | 2462.00 | 2462.00 | True | 134 | 10.28 | 10 | 10 |  |  |  |  |  | [2462.0] |
| hill_climbing | hill_climbing/random_restart_hc_3.json | random_restart_hc | random_restart_hc | default | 3 | 1039.00 | 2338.00 | 2338.00 | True | 146 | 10.77 | 10 | 10 |  |  |  |  |  | [2338.0] |
| hill_climbing | hill_climbing/sideways_move_hc_1.json | sideways_move_hc | sideways_move_hc | default | 1 | 879.00 | 2406.00 | 2406.00 | True | 124 | 9.12 |  |  | 100 | 100 |  |  |  | [2406.0] |
| hill_climbing | hill_climbing/sideways_move_hc_2.json | sideways_move_hc | sideways_move_hc | default | 2 | 1107.00 | 2403.00 | 2403.00 | True | 117 | 8.42 |  |  | 100 | 100 |  |  |  | [2403.0] |
| hill_climbing | hill_climbing/sideways_move_hc_3.json | sideways_move_hc | sideways_move_hc | default | 3 | 1039.00 | 2376.00 | 2376.00 | True | 122 | 8.87 |  |  | 100 | 100 |  |  |  | [2376.0] |
| hill_climbing | hill_climbing/steepest_ascent_hc_1.json | steepest_ascent_hc | steepest_ascent_hc | default | 1 | 879.00 | 2243.00 | 2243.00 | True | 16 | 1.25 |  |  |  |  |  |  |  | [2243.0] |
| hill_climbing | hill_climbing/steepest_ascent_hc_2.json | steepest_ascent_hc | steepest_ascent_hc | default | 2 | 1107.00 | 2265.00 | 2265.00 | True | 14 | 1.03 |  |  |  |  |  |  |  | [2265.0] |
| hill_climbing | hill_climbing/steepest_ascent_hc_3.json | steepest_ascent_hc | steepest_ascent_hc | default | 3 | 1039.00 | 2279.00 | 2279.00 | True | 18 | 1.34 |  |  |  |  |  |  |  | [2279.0] |
| hill_climbing | hill_climbing/stochastic_hc_1.json | stochastic_hc | stochastic_hc | default | 1 | 879.00 | 2169.00 | 2169.00 | True | 29 | 2.10 |  |  |  |  |  |  |  | [2169.0] |
| hill_climbing | hill_climbing/stochastic_hc_2.json | stochastic_hc | stochastic_hc | default | 2 | 1107.00 | 2126.00 | 2126.00 | True | 25 | 1.87 |  |  |  |  |  |  |  | [2126.0] |
| hill_climbing | hill_climbing/stochastic_hc_3.json | stochastic_hc | stochastic_hc | default | 3 | 1039.00 | 2283.00 | 2283.00 | True | 27 | 2.02 |  |  |  |  |  |  |  | [2283.0] |
| simulated_annealing | simulated_annealing/simulated_annealing_1.json | simulated_annealing | simulated_annealing | default | 1 | 879.00 | 2584.00 | 2584.00 | True | 42582 | 19.05 |  |  |  |  | 65 |  |  | [2584.0] |
| simulated_annealing | simulated_annealing/simulated_annealing_2.json | simulated_annealing | simulated_annealing | default | 2 | 1107.00 | 2615.00 | 2615.00 | True | 42582 | 20.34 |  |  |  |  | 69 |  |  | [2615.0] |
| simulated_annealing | simulated_annealing/simulated_annealing_3.json | simulated_annealing | simulated_annealing | default | 3 | 1039.00 | 2615.00 | 2615.00 | True | 42582 | 19.11 |  |  |  |  | 64 |  |  | [2615.0] |
