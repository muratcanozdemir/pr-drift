import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import replay


class TestReplayArgs(unittest.TestCase):
    def test_requires_repo(self):
        with patch.object(sys, "argv", ["replay.py"]), self.assertRaises(SystemExit):
            replay.parse_args()

    def test_defaults(self):
        with patch.object(sys, "argv", ["replay.py", "--repo", "/tmp/repo"]):
            args = replay.parse_args()

        self.assertEqual(args.repo, "/tmp/repo")
        self.assertEqual(args.pr_list, "pr_list.json")
        self.assertEqual(args.db, "replay.db")

    def test_overrides(self):
        argv = [
            "replay.py",
            "--repo", "/tmp/repo",
            "--pr-list", "prs.json",
            "--db", "out.db",
        ]
        with patch.object(sys, "argv", argv):
            args = replay.parse_args()

        self.assertEqual(args.pr_list, "prs.json")
        self.assertEqual(args.db, "out.db")

    @patch("replay.subprocess.check_output")
    def test_get_diff_invokes_git_show(self, mock_check_output):
        mock_check_output.return_value = b"diff content"

        result = replay.get_diff("/repo", "abc123")

        mock_check_output.assert_called_once_with(
            ["git", "show", "--format=", "abc123"], cwd="/repo"
        )
        self.assertEqual(result, b"diff content")


if __name__ == "__main__":
    unittest.main()
