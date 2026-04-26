from __future__ import annotations

import unittest


class Goal974RemainingLocalBaselinesTest(unittest.TestCase):
    def test_remaining_baselines_are_valid_after_linux_postgis_collection(self) -> None:
        module = __import__("scripts.goal836_rtx_baseline_readiness_gate", fromlist=["analyze_plan"])
        payload = module.analyze_plan()
        self.assertEqual(payload["invalid_artifact_count"], 0)

        rows = {
            (row["app"], row["path_name"]): row
            for row in payload["rows"]
        }
        expected_remaining_missing: dict[tuple[str, str], set[str]] = {}
        all_missing = {
            (row["app"], row["path_name"], check["baseline"])
            for row in payload["rows"]
            for check in row["artifact_checks"]
            if check["status"] == "missing"
        }
        self.assertEqual(
            all_missing,
            {
                (app, path_name, baseline)
                for (app, path_name), baselines in expected_remaining_missing.items()
                for baseline in baselines
            },
        )
        for row in rows.values():
            with self.subTest(app=row["app"], path=row["path_name"]):
                self.assertFalse(
                    [check for check in row["artifact_checks"] if check["status"] == "missing"]
                )
                self.assertFalse(
                    [check for check in row["artifact_checks"] if check["status"] == "invalid"]
                )

    def test_goal971_stays_conservative_after_partial_baseline_collection(self) -> None:
        module = __import__(
            "scripts.goal971_post_goal969_baseline_speedup_review_package",
            fromlist=["build_package"],
        )
        payload = module.build_package()
        self.assertEqual(payload["same_semantics_baselines_complete_count"], 17)
        self.assertEqual(payload["baseline_pending_count"], 0)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)


if __name__ == "__main__":
    unittest.main()
