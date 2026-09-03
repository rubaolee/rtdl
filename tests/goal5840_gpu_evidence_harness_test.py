from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts import goal5840_freeze_gpu_inputs as freezer
from scripts.goal5840_gpu_cases import goal5840_mode_cases


class Goal5840GpuEvidenceHarnessTest(unittest.TestCase):
    def test_four_cases_are_deterministic_and_non_degenerate(self) -> None:
        first = goal5840_mode_cases()
        second = goal5840_mode_cases()
        self.assertEqual([row.key for row in first], [row.key for row in second])
        self.assertEqual(
            [row.route.plan.plan_sha256 for row in first],
            [row.route.plan.plan_sha256 for row in second],
        )
        self.assertEqual(
            [row.expected_output for row in first],
            [
                ((100, 10), (100, 30), (200, 20)),
                5,
                35,
                {
                    "schema": "rtdl.v4.sphere_any_hit_count_output.v1",
                    "counts": [4, 1, 1, 0, 4, 0],
                },
            ],
        )

    def test_authority_has_three_routes_four_modes_and_zero_gpu_runs(self) -> None:
        document = freezer.build_authority("2026-09-03T00:00:00Z")
        self.assertEqual(document["route_bundle_group_count"], 3)
        self.assertEqual(document["required_mode_count"], 4)
        self.assertEqual(len(document["mode_cases"]), 4)
        self.assertEqual(
            document["execution_counts_at_freeze"]["goal5840_gpu_launches"], 0
        )
        body = dict(document)
        observed = body.pop("authority_sha256")
        body["authority_sha256"] = ""
        expected = hashlib.sha256(
            freezer.DOMAIN
            + json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        self.assertEqual(observed, expected)
        for row in document["mode_cases"]:
            self.assertRegex(row["declaration_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(
                row["control_flow_manifest_sha256"], r"^[0-9a-f]{64}$"
            )

    def test_capture_runner_requires_committed_pre_pod_authority(self) -> None:
        source = Path(
            "scripts/goal5840_capture_gpu_evidence.py"
        ).read_text(encoding="utf-8")
        self.assertIn("PRE_POD_INPUT_AUTHORITY.json", source)
        self.assertIn("_verify_pre_pod_authority()", source)
        self.assertIn('sys.executable,\n            "-I"', source)
        self.assertIn("EXACT_BUNDLE_MUTATION_RESULT.json", source)


if __name__ == "__main__":
    unittest.main()
