import re
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from visualization import app


def test_vendor_scripts_exist():
    for name in app.VENDOR_SCRIPTS:
        assert (app.VENDOR_DIR / name).stat().st_size > 10_000


def test_rendered_html_is_self_contained():
    html = app.render_html()
    assert "<!--VENDOR_SCRIPTS-->" not in html
    assert not re.findall(r"<script[^>]+src=", html)
    assert "https://cdn" not in html and "googleapis" not in html
    assert "THREE" in html and "OrbitControls" in html


def test_server_serves_self_contained_page():
    server = ThreadingHTTPServer(("127.0.0.1", 0), app.VisualizerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_address[1]}/") as response:
            body = response.read().decode("utf-8")
        assert "OrbitControls" in body and "runSelect" in body
    finally:
        server.shutdown()
        server.server_close()


def test_dropped_connection_is_silent(monkeypatch):
    handler = app.VisualizerHandler.__new__(app.VisualizerHandler)

    def broken_route():
        raise BrokenPipeError

    monkeypatch.setattr(handler, "_route", broken_route)
    handler.do_GET()
