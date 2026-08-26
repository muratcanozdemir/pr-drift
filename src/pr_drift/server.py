import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from pr_drift.detector import PRDriftDetector
from pr_drift.github import fetch_pr_diff
from pr_drift.storage import Storage


def handle_webhook(payload: dict, detector: PRDriftDetector, store: Storage, token: str) -> dict | None:
    """Score an incoming PR webhook payload. Returns metrics, or None if ignored."""
    if payload.get("action") != "opened":
        return None

    pr = payload["pull_request"]
    owner = payload["repository"]["owner"]["login"]
    repo = payload["repository"]["name"]
    pr_number = pr["number"]

    diff = fetch_pr_diff(owner, repo, pr_number, token=token)
    metrics = detector.observe(diff)

    store.record(
        owner=owner,
        repo=repo,
        pr_number=pr_number,
        diff_bytes=len(diff),
        score=metrics["score"],
        z_score=metrics["z_score"],
    )

    return metrics


class Handler(BaseHTTPRequestHandler):
    detector: PRDriftDetector = None
    store: Storage = None

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))
        token = os.environ.get("GITHUB_TOKEN", "")

        try:
            metrics = handle_webhook(payload, self.detector, self.store, token)
        except Exception as exc:  # noqa: BLE001 - handler boundary must always respond, never crash the thread
            print("error handling webhook:", exc)
            self.send_response(500)
            self.end_headers()
            return

        if metrics is not None:
            print("PR", payload["pull_request"]["number"], metrics)

        self.send_response(200)
        self.end_headers()


def main():
    Handler.detector = PRDriftDetector()
    Handler.store = Storage()
    HTTPServer(("", 8000), Handler).serve_forever()


if __name__ == "__main__":
    main()
