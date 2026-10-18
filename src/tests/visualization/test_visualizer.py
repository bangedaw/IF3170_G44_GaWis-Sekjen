import json
from pathlib import Path

import pytest
from matplotlib.figure import Figure

from visualization import app, state_view

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
MOCK_FILES = [
    "mock_genetic_algorithm.json",
    "mock_multi_truck_simulated_annealing.json",
    "mock_random_restart_hc.json",
    "mock_sideways_move_hc.json",
    "mock_simulated_annealing.json",
    "mock_steepest_ascent_hc.json",
]


@pytest.mark.parametrize("mock_name", MOCK_FILES)
def test_state_summary_on_all_mocks(mock_name):
    mock_path = FIXTURES_DIR / mock_name
    data = json.loads(mock_path.read_text(encoding="utf-8"))
    problem = data["problem"]
    final_state = data["final_state"]

    summary = state_view.state_summary(problem, final_state)
    assert isinstance(summary, dict)
    assert "total_value" in summary
    assert "feasible" in summary
    assert "trucks" in summary
    assert len(summary["trucks"]) == len(problem["trucks"])
    assert "inside_packages" in summary
    assert "outside_packages" in summary
    assert summary["inside_count"] + summary["outside_count"] == len(problem["packages"])


@pytest.mark.parametrize("mock_name", MOCK_FILES)
def test_render_figures_on_all_mocks(mock_name):
    mock_path = FIXTURES_DIR / mock_name
    data = json.loads(mock_path.read_text(encoding="utf-8"))
    problem = data["problem"]
    initial_state = data["initial_state"]
    final_state = data["final_state"]

    fig1 = state_view.render_state_figure(problem, final_state)
    assert isinstance(fig1, Figure)

    fig2 = state_view.render_state_comparison(problem, initial_state, final_state)
    assert isinstance(fig2, Figure)


def test_state_to_3d_data():
    mock_path = FIXTURES_DIR / "mock_multi_truck_simulated_annealing.json"
    data = json.loads(mock_path.read_text(encoding="utf-8"))
    d3 = state_view.state_to_3d_data(data["problem"], data["final_state"])

    assert "palette" in d3
    assert "trucks" in d3
    assert len(d3["trucks"]) == 2
    for t in d3["trucks"]:
        assert "dimensions" in t
        assert "max_capacity" in t


def test_app_find_and_load_runs():
    runs = app.find_all_runs([FIXTURES_DIR])
    assert len(runs) >= 6

    target_run = runs[0]
    details = app.load_run_details(target_run["path"])
    assert "metadata" in details
    assert "initial_summary" in details
    assert "final_summary" in details


def test_app_render_plot_image():
    mock_rel = "src/tests/fixtures/mock_genetic_algorithm.json"
    img = app.render_plot_image_bytes(mock_rel, plot_type="ga")
    assert len(img) > 1000
    assert img[:8] == b"\x89PNG\r\n\x1a\n"
