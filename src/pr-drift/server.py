from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pr_drift.detector import PRDriftDetector
from pr_drift.github import fetch_pr_diff

detector = PRDriftDetector()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))

        if payload.get("action") != "opened":
            return

        pr = payload["pull_request"]
        owner = payload["repository"]["owner"]["login"]
        repo = payload["repository"]["name"]
        pr_number = pr["number"]

        diff = fetch_pr_diff(owner, repo, pr_number, token="ENV_GITHUB_TOKEN")
        metrics = detector.observe(diff)

        store.record(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            diff_bytes=len(diff),
            score=metrics["score"],
            z_score=metrics["z_score"],
        )

        print("PR", pr_number, metrics)

        self.send_response(200)
        self.end_headers()

HTTPServer(("", 8000), Handler).serve_forever()
