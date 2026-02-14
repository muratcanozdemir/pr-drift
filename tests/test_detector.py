import unittest
from pr_drift.detector import PRDriftDetector


class TestPRDriftDetector(unittest.TestCase):

    def setUp(self):
        self.detector = PRDriftDetector(
            window_bytes=100_000,
            rebuild_every=5,
        )

    def test_cold_start(self):
        diff = b"diff --git a/foo.py b/foo.py\n+print('hi')"
        metrics = self.detector.observe(diff)
        self.assertEqual(metrics["score"], 0.0)
        self.assertEqual(metrics["z_score"], 0.0)

    def test_repeated_diff(self):
        diff = b"diff --git a/foo.py b/foo.py\n+print('hi')"

        scores = []
        for _ in range(20):
            metrics = self.detector.observe(diff)
            scores.append(metrics["score"])

        # After warmup, scores should converge
        self.assertLess(max(scores[10:]) - min(scores[10:]), 0.01)

    def test_novel_diff(self):
        base = b"diff --git a/foo.py b/foo.py\n+print('hi')"
        novel = b"diff --git a/app.js b/app.js\n+import React from 'react'\n" * 50

        for _ in range(20):
            self.detector.observe(base)

        metrics = self.detector.observe(novel)
        self.assertGreater(metrics["score"], 0.5)

    def test_size_bias(self):
        small = b"a\n" * 100
        large = b"a\n" * 10_000

        for _ in range(20):
            self.detector.observe(small)

        s1 = self.detector.observe(small)["score"]
        s2 = self.detector.observe(large)["score"]

        # Compression ratio should be similar for same structure
        self.assertAlmostEqual(s1, s2, delta=0.05)

    def test_rebuild_stability(self):
        diff = b"diff --git a/foo.py b/foo.py\n+print('hi')"

        for _ in range(50):
            self.detector.observe(diff)

        metrics1 = self.detector.observe(diff)
        metrics2 = self.detector.observe(diff)

        # Rebuild should not cause wild jumps
        self.assertAlmostEqual(
            metrics1["score"],
            metrics2["score"],
            delta=0.05
        )


if __name__ == "__main__":
    unittest.main()
