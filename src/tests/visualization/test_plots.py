import json
from pathlib import Path

import pytest
from matplotlib.figure import Figure

from visualization.plots import (generate_plots, load_run, plot_acceptance_prob, plot_compare, plot_ga,
                                 plot_objective)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
HC = ["mock_steepest_ascent_hc", "mock_sideways_move_hc", "mock_random_restart_hc"]


def fixture(name):
    return FIXTURES / f"{name}.json"


def is_png(path):
    return path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("name", HC + ["mock_simulated_annealing", "mock_multi_truck_simulated_annealing"])
def test_plot_objective_accepts_path_dict_and_saves_png(name, tmp_path):
    fig = plot_objective(fixture(name), save=tmp_path / "o.png")
    assert isinstance(fig, Figure) and is_png(tmp_path / "o.png")
    assert isinstance(plot_objective(load_run(fixture(name))), Figure)


def test_plot_objective_draws_one_line_with_history_length():
    run = load_run(fixture("mock_steepest_ascent_hc"))
    ax = plot_objective(run).axes[0]
    assert len(ax.lines[0].get_ydata()) == len(run["history"]["objective"])


def test_plot_acceptance_prob_for_sa(tmp_path):
    run = load_run(fixture("mock_simulated_annealing"))
    fig = plot_acceptance_prob(run, save=tmp_path / "a.png")
    assert len(fig.axes[0].lines[0].get_ydata()) == len(run["history"]["acceptance_prob"])
    assert "stuck" in fig.axes[0].get_title() and is_png(tmp_path / "a.png")


def test_plot_acceptance_prob_rejects_non_sa():
    with pytest.raises(ValueError):
        plot_acceptance_prob(fixture("mock_steepest_ascent_hc"))


def test_plot_ga_draws_max_and_avg(tmp_path):
    run = load_run(fixture("mock_genetic_algorithm"))
    fig = plot_ga(run, save=tmp_path / "g.png")
    ax = fig.axes[0]
    assert len(ax.lines) == 2 and len(ax.lines[0].get_ydata()) == len(run["history"]["max"])
    assert "populasi" in ax.get_title() and is_png(tmp_path / "g.png")


def test_plot_ga_rejects_non_ga():
    with pytest.raises(ValueError):
        plot_ga(fixture("mock_simulated_annealing"))


def test_plot_compare_groups_runs_by_label(tmp_path):
    runs = [load_run(fixture(n)) for n in HC]
    runs += [dict(runs[0], final_objective=runs[0]["final_objective"] + 5, duration_sec=1.0)]
    fig = plot_compare(runs, save=tmp_path / "c.png")
    assert len(fig.axes) == 3 and is_png(tmp_path / "c.png")
    assert len(fig.axes[0].patches) == len({r.get("label") or r["algorithm"] for r in runs})


def test_plot_compare_value_panel_ignores_objective_scale():
    base = load_run(fixture("mock_steepest_ascent_hc"))
    runs = [dict(base, label="default", final_objective=100.0, final_value=100.0),
            dict(base, label="alt", final_objective=5000.0, final_value=90.0)]
    fig = plot_compare(runs)
    objective, value, duration = fig.axes
    assert [round(p.get_height()) for p in objective.patches] == [100, 5000]
    assert [round(p.get_height()) for p in value.patches] == [100, 90]
    assert value.get_title() == "Total value akhir" and duration.get_title() == "Durasi pencarian"


def test_plot_compare_custom_grouping_and_empty():
    runs = [load_run(fixture(n)) for n in HC]
    assert len(plot_compare(runs, group_by=lambda r: "semua").axes[0].patches) == 1
    with pytest.raises(ValueError):
        plot_compare([])


def test_generate_plots_walks_output_folder(tmp_path):
    for name, folder in (("mock_steepest_ascent_hc", "hill_climbing"), ("mock_sideways_move_hc", "hill_climbing"),
                         ("mock_simulated_annealing", "simulated_annealing"),
                         ("mock_genetic_algorithm", "genetic_algorithm")):
        target = tmp_path / folder / f"{name}.json"
        target.parent.mkdir(exist_ok=True)
        target.write_text(fixture(name).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "bukan_run.json").write_text(json.dumps({"hello": 1}), encoding="utf-8")

    written = generate_plots(tmp_path)
    names = {p.relative_to(tmp_path / "plots").as_posix() for p in written}
    assert names == {
        "hill_climbing/mock_steepest_ascent_hc_objective.png",
        "hill_climbing/mock_sideways_move_hc_objective.png",
        "hill_climbing/compare.png",
        "simulated_annealing/mock_simulated_annealing_objective.png",
        "simulated_annealing/mock_simulated_annealing_acceptance.png",
        "genetic_algorithm/mock_genetic_algorithm_ga.png",
    }
    assert all(is_png(p) for p in written)
    assert generate_plots(tmp_path) == written
