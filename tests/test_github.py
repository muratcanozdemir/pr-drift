import unittest
from unittest.mock import MagicMock, patch

from pr_drift.github import fetch_pr_diff


class TestFetchPrDiff(unittest.TestCase):
    @patch("pr_drift.github.urllib.request.urlopen")
    def test_builds_request_with_auth_and_diff_headers(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"diff --git a/f b/f\n"
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = fetch_pr_diff("acme", "widgets", 7, token="secret")

        self.assertEqual(result, b"diff --git a/f b/f\n")

        sent_request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            sent_request.full_url,
            "https://api.github.com/repos/acme/widgets/pulls/7",
        )
        self.assertEqual(sent_request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(
            sent_request.get_header("Accept"), "application/vnd.github.v3.diff"
        )

        _, kwargs = mock_urlopen.call_args
        self.assertEqual(kwargs.get("timeout"), 10)


if __name__ == "__main__":
    unittest.main()
