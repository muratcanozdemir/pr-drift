import argparse
import json
import subprocess

from pr_drift.detector import PRDriftDetector
from pr_drift.storage import Storage


def get_diff(repo_path, commit):
    """
    Diff between merge commit and its first parent.
    """
    cmd = ["git", "show", "--format=", commit]
    out = subprocess.check_output(cmd, cwd=repo_path)
    return out


def parse_args():
    parser = argparse.ArgumentParser(description="Replay PR drift scores over repo history.")
    parser.add_argument("--repo", required=True, help="Path to the git repository to replay.")
    parser.add_argument(
        "--pr-list",
        default="pr_list.json",
        help="JSON file with a list of {pr, merge_commit} entries.",
    )
    parser.add_argument("--db", default="replay.db", help="SQLite database path for results.")
    return parser.parse_args()


def main():
    args = parse_args()

    detector = PRDriftDetector()
    store = Storage(args.db)

    with open(args.pr_list) as f:
        prs = json.load(f)

    for item in prs:
        pr = item["pr"]
        commit = item["merge_commit"]

        diff = get_diff(args.repo, commit)
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
