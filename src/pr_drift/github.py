# github.py
import urllib.request


def fetch_pr_diff(owner, repo, pr_number, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github.v3.diff")

    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()
