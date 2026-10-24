"""Check reachability of Where Next's registered official source websites."""

import concurrent.futures
import datetime as dt
import json
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "site" / "data" / "sources.json"
HEALTH_FILE = ROOT / "site" / "data" / "source-health.json"
TIMEOUT_SECONDS = 15


def check(source):
    request = urllib.request.Request(
        source["url"],
        headers={"User-Agent": "WhereNextSourceStatus/1.0 (+https://sergosangreal-oss.github.io/where-next/)"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return {"ok": 200 <= response.status < 400, "status": response.status, "url": response.geturl()}
    except urllib.error.HTTPError as error:
        if error.code in (403, 405, 501):
            try:
                get_request = urllib.request.Request(
                    source["url"],
                    headers={"User-Agent": "WhereNextSourceStatus/1.0", "Range": "bytes=0-0"},
                )
                with urllib.request.urlopen(get_request, timeout=TIMEOUT_SECONDS) as response:
                    return {"ok": 200 <= response.status < 400, "status": response.status, "url": response.geturl()}
            except Exception as fallback_error:  # noqa: BLE001
                return {"ok": False, "status": getattr(fallback_error, "code", None), "error": type(fallback_error).__name__}
        return {"ok": False, "status": error.code, "error": "HTTP error"}
    except Exception as error:  # noqa: BLE001
        return {"ok": False, "status": None, "error": type(error).__name__}


def main():
    payload = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    sources = payload.get("sources", [])
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(check, sources))
    health = {
        "checkedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "total": len(sources),
        "reachable": sum(1 for result in results if result["ok"]),
        "sources": {source["url"]: result for source, result in zip(sources, results)},
    }
    HEALTH_FILE.write_text(json.dumps(health, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {health['total']} source URLs; {health['reachable']} responded successfully.")


if __name__ == "__main__":
    main()
