"""Desktop launcher: starts the API + UI and opens a browser."""

from __future__ import annotations

import threading
import time
import webbrowser

import uvicorn

from config.settings import settings


def _open_when_ready(url: str, timeout_s: float = 90.0) -> None:
    import urllib.request

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url + "/api/health", timeout=2) as res:
                if res.status == 200:
                    webbrowser.open(url)
                    return
        except Exception:
            time.sleep(0.8)
    webbrowser.open(url)


def main() -> None:
    host = "127.0.0.1"
    port = int(settings.PORT)
    url = f"http://{host}:{port}"
    print("GeoProduction AI — SIH 2026 PS 26009")
    print(f"Starting decision-support server at {url}")
    threading.Thread(target=_open_when_ready, args=(url,), daemon=True).start()
    uvicorn.run("src.api.main:app", host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    main()
