import unittest
from unittest.mock import MagicMock, patch

from pr_drift.server import handle_webhook


class TestHandleWebhook(unittest.TestCase):
    def setUp(self):
        self.detector = MagicMock()
        self.detector.observe.return_value = {"score": 0.5, "z_score": 1.0}
        self.store = MagicMock()

        self.payload = {
            "action": "opened",
            "pull_request": {"number": 7},
            "repository": {"owner": {"login": "acme"}, "name": "widgets"},
        }

    def test_ignores_non_opened_actions(self):
        payload = {**self.payload, "action": "closed"}
        result = handle_webhook(payload, self.detector, self.store, token="t")

        self.assertIsNone(result)
        self.detector.observe.assert_not_called()
        self.store.record.assert_not_called()

    @patch("pr_drift.server.fetch_pr_diff")
    def test_scores_and_records_opened_pr(self, mock_fetch):
        mock_fetch.return_value = b"diff --git a/f b/f\n+x"

        result = handle_webhook(self.payload, self.detector, self.store, token="tok")

        mock_fetch.assert_called_once_with("acme", "widgets", 7, token="tok")
        self.detector.observe.assert_called_once_with(b"diff --git a/f b/f\n+x")
        self.store.record.assert_called_once_with(
            owner="acme",
            repo="widgets",
            pr_number=7,
            diff_bytes=len(b"diff --git a/f b/f\n+x"),
            score=0.5,
            z_score=1.0,
        )
        self.assertEqual(result, {"score": 0.5, "z_score": 1.0})


if __name__ == "__main__":
    unittest.main()
