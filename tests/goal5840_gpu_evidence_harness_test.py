from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import goal5840_freeze_gpu_inputs as freezer
from scripts import goal5840_freeze_attempt02_repair_inputs as attempt02_freezer
from scripts import goal5840_freeze_attempt03_repair_inputs as attempt03_freezer
from scripts import goal5840_freeze_attempt04_repair_inputs as attempt04_freezer
from scripts import goal5840_freeze_repair_inputs as repair_freezer
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
        self.assertIn("POST_ATTEMPT_01_REPAIR_AUTHORITY.json", source)
        self.assertIn("_verify_repair_authority(", source)
        self.assertIn("POST_ATTEMPT_02_REPAIR_AUTHORITY.json", source)
        self.assertIn("_verify_attempt02_repair_authority(", source)
        self.assertIn("POST_ATTEMPT_03_REPAIR_AUTHORITY.json", source)
        self.assertIn("POST_ATTEMPT_04_REPAIR_AUTHORITY.json", source)
        self.assertIn("_verify_attempt04_repair_authority(", source)
        self.assertIn("rtdl.goal5840.true_optix_target_evidence.v5", source)
        self.assertIn('sys.executable,\n            "-I"', source)
        self.assertIn("EXACT_BUNDLE_MUTATION_RESULT.json", source)

    def test_repair_authority_is_append_only_and_preserves_scientific_inputs(
        self,
    ) -> None:
        expected_before_output = tuple(
            path
            for path in repair_freezer.ALLOWED_CHANGED_PATHS
            if not path.endswith("POST_ATTEMPT_01_REPAIR_AUTHORITY.json")
        )
        with patch.object(Path, "exists", return_value=False), patch.object(
            repair_freezer,
            "_changed_paths_since_base",
            return_value=expected_before_output,
        ):
            document = repair_freezer.build_authority("2026-09-03T10:00:00Z")
        original = json.loads(
            repair_freezer.PRE_POD_AUTHORITY.read_text(encoding="ascii")
        )
        self.assertEqual(document["mode_cases"], original["mode_cases"])
        self.assertEqual(
            document["goal5838_frozen_core"],
            original["goal5838_frozen_core"],
        )
        self.assertEqual(
            document["execution_counts_at_repair_freeze"][
                "accepted_goal5840_positive_evidence_rows"
            ],
            0,
        )
        self.assertEqual(
            document["base_attempt"]["source_commit"],
            repair_freezer.BASE_COMMIT,
        )
        self.assertEqual(
            document["repair_scope"]["exact_changed_paths_since_base"],
            list(repair_freezer.ALLOWED_CHANGED_PATHS),
        )
        body = dict(document)
        observed = body["authority_sha256"]
        body["authority_sha256"] = ""
        expected = hashlib.sha256(
            repair_freezer.DOMAIN
            + json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        self.assertEqual(observed, expected)

    def test_attempt03_repair_authority_preserves_all_failures_and_inputs(
        self,
    ) -> None:
        expected_before_output = tuple(
            path
            for path in attempt03_freezer.ALLOWED_CHANGED_PATHS
            if not path.endswith("POST_ATTEMPT_03_REPAIR_AUTHORITY.json")
        )

        def changed_paths(base: str, revision: str | None = None):
            if revision is None:
                self.assertEqual(base, attempt03_freezer.BASE_COMMIT)
                return expected_before_output
            self.assertEqual(revision, attempt03_freezer.BASE_COMMIT)
            return tuple(sorted(attempt02_freezer.ALLOWED_CHANGED_PATHS))

        with patch.object(Path, "exists", return_value=False), patch.object(
            attempt03_freezer,
            "_changed_paths",
            side_effect=changed_paths,
        ):
            document = attempt03_freezer.build_authority(
                "2026-09-03T11:00:00Z"
            )
        prior = json.loads(
            attempt03_freezer.PRIOR_REPAIR_AUTHORITY.read_text(encoding="ascii")
        )
        self.assertEqual(document["mode_cases"], prior["mode_cases"])
        self.assertEqual(
            document["goal5838_frozen_core"], prior["goal5838_frozen_core"]
        )
        counts = document["base_chain"][
            "formal_observed_counts_through_attempt_03"
        ]
        self.assertEqual(counts["runner_processes_started"], 3)
        self.assertEqual(counts["published_evidence_bundles"], 1)
        self.assertEqual(counts["independently_accepted_reports"], 0)
        self.assertEqual(counts["accepted_positive_evidence_rows"], 0)
        artifacts = document["base_chain"]["attempt_03_incident"][
            "published_failure_artifacts"
        ]
        self.assertEqual(len(artifacts), 2)
        self.assertEqual(
            document["repair_scope"]["exact_changed_paths_since_base"],
            list(attempt03_freezer.ALLOWED_CHANGED_PATHS),
        )
        body = dict(document)
        observed = body["authority_sha256"]
        body["authority_sha256"] = ""
        expected = hashlib.sha256(
            attempt03_freezer.DOMAIN
            + json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        self.assertEqual(observed, expected)

    def test_attempt04_repair_authority_preserves_partial_acceptance_and_inputs(
        self,
    ) -> None:
        expected_before_output = tuple(
            path
            for path in attempt04_freezer.ALLOWED_CHANGED_PATHS
            if not path.endswith("POST_ATTEMPT_04_REPAIR_AUTHORITY.json")
        )

        def changed_paths(base: str, revision: str | None = None):
            if revision is None:
                self.assertEqual(base, attempt04_freezer.BASE_COMMIT)
                return expected_before_output
            self.assertEqual(base, attempt03_freezer.BASE_COMMIT)
            self.assertEqual(revision, attempt04_freezer.BASE_COMMIT)
            return tuple(sorted(attempt03_freezer.ALLOWED_CHANGED_PATHS))

        with patch.object(Path, "exists", return_value=False), patch.object(
            attempt04_freezer,
            "_changed_paths",
            side_effect=changed_paths,
        ):
            document = attempt04_freezer.build_authority(
                "2026-09-03T12:00:00Z"
            )
        prior = json.loads(
            attempt04_freezer.PRIOR_REPAIR_AUTHORITY.read_text(encoding="ascii")
        )
        self.assertEqual(document["mode_cases"], prior["mode_cases"])
        self.assertEqual(
            document["goal5838_frozen_core"], prior["goal5838_frozen_core"]
        )
        counts = document["base_chain"][
            "formal_observed_counts_through_attempt_04"
        ]
        self.assertEqual(counts["runner_processes_started"], 4)
        self.assertEqual(counts["published_evidence_bundles"], 3)
        self.assertEqual(counts["independently_accepted_per_mode_reports"], 1)
        self.assertEqual(counts["accepted_complete_goal5840_results"], 0)
        artifacts = document["base_chain"]["attempt_04_incident"][
            "published_failure_artifacts"
        ]
        self.assertEqual(len(artifacts), 4)
        self.assertEqual(artifacts[1]["verdict"], "ACCEPT")
        self.assertEqual(artifacts[3]["verdict"], "REJECT")
        self.assertEqual(
            document["repair_scope"]["exact_changed_paths_since_base"],
            list(attempt04_freezer.ALLOWED_CHANGED_PATHS),
        )
        body = dict(document)
        observed = body["authority_sha256"]
        body["authority_sha256"] = ""
        expected = hashlib.sha256(
            attempt04_freezer.DOMAIN
            + json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        self.assertEqual(observed, expected)

    def test_attempt02_repair_authority_preserves_both_failures_and_inputs(
        self,
    ) -> None:
        expected_before_output = tuple(
            path
            for path in attempt02_freezer.ALLOWED_CHANGED_PATHS
            if not path.endswith("POST_ATTEMPT_02_REPAIR_AUTHORITY.json")
        )

        def changed_paths(base: str, revision: str | None = None):
            if revision is None:
                self.assertEqual(base, attempt02_freezer.BASE_COMMIT)
                return expected_before_output
            self.assertEqual(revision, attempt02_freezer.BASE_COMMIT)
            return tuple(sorted(repair_freezer.ALLOWED_CHANGED_PATHS))

        with patch.object(Path, "exists", return_value=False), patch.object(
            attempt02_freezer,
            "_changed_paths",
            side_effect=changed_paths,
        ):
            document = attempt02_freezer.build_authority(
                "2026-09-03T10:30:00Z"
            )
        prior = json.loads(
            attempt02_freezer.PRIOR_REPAIR_AUTHORITY.read_text(encoding="ascii")
        )
        self.assertEqual(document["mode_cases"], prior["mode_cases"])
        self.assertEqual(
            document["goal5838_frozen_core"], prior["goal5838_frozen_core"]
        )
        self.assertEqual(
            document["base_chain"]["formal_observed_counts_through_attempt_02"]
            ["runner_processes_started"],
            2,
        )
        self.assertEqual(
            document["base_chain"]["post_failure_diagnostics"]
            ["diagnostic_mode_executions"],
            2,
        )
        self.assertEqual(
            document["execution_counts_at_repair_freeze"]
            ["accepted_goal5840_positive_evidence_rows"],
            0,
        )
        self.assertEqual(
            document["repair_scope"]["exact_changed_paths_since_base"],
            list(attempt02_freezer.ALLOWED_CHANGED_PATHS),
        )
        body = dict(document)
        observed = body["authority_sha256"]
        body["authority_sha256"] = ""
        expected = hashlib.sha256(
            attempt02_freezer.DOMAIN
            + json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
