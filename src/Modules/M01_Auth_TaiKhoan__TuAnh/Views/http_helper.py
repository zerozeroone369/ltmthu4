"""Shared HTTP JSON & background Tkinter runner for Tú Anh Desktop Views."""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request


def http_json(url: str, method: str = "GET", body: dict | None = None, token: str = "") -> tuple[int, dict]:
    """Perform a synchronous JSON HTTP request using Python stdlib urllib."""
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"detail": raw or str(err)}
        return err.code, parsed


def run_async_tk(widget, fn, on_done) -> None:
    """Run blocking network call in a daemon thread and schedule callback on Tk main loop."""

    def worker():
        try:
            result = fn()
        except (urllib.error.URLError, OSError, ValueError) as exc:
            result = (0, {"detail": f"Lỗi kết nối Server: {exc}"})

        def finish():
            if widget.winfo_exists():
                on_done(result)

        widget.after(0, finish)

    threading.Thread(target=worker, daemon=True).start()
