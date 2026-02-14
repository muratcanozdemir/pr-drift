import json
import subprocess
from pr_drift.detector import PRDriftDetector
from pr_drift.storage import Storage


REPO_PATH = "/path/to/repo"
PR_LIST = "pr_list.json"
DB_PATH = "replay.db"


def get_diff(commit):
    """
    Diff between merge commit and its first parent.
    """
    cmd = ["git", "show", "--format=", commit]
    out = subprocess.check_output(cmd, cwd=REPO_PATH)
    return out


def main():
    detector = PRDriftDetector()
    store = Storage(DB_PATH)

    with open(PR_LIST) as f:
        prs = json.load(f)

    for item in prs:
        pr = item["pr"]
        commit = item["merge_commit"]

        diff = get_diff(commit)
        metrics = detector.observe(diff)

        store.record(
            owner="local",
            repo="replay",
            pr_number=pr,
            diff_bytes=len(diff),
            score=metrics["score"],
            z_score=metrics["z_score"],
        )

        print(
            f"PR {pr:4d} "
            f"score={metrics['score']:.3f} "
            f"z={metrics['z_score']:.2f}"
        )


if __name__ == "__main__":
    main()
