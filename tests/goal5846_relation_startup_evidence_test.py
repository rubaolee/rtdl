from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from experiments.goal5846_relation_startup.worker import PYOPTIX_ARM, RTDL_ARM
from scripts import goal5846_run_relation_startup_comparison as runner


class Goal5846RelationStartupEvidenceTest(unittest.TestCase):
    def test_frozen_preregistration_and_balanced_schedule(self) -> None:
        path = Path(
            "history/internal_docs/goal5846_relation_startup_20260905/"
            "PREREGISTRATION.json"
        )
        value = runner._validate_preregistration(
            path,
            SimpleNamespace(blocks=8, warmups=16, repetitions=128),
        )
        self.assertEqual(
            value["preregistration_sha256"],
            "53111d83efc13497edae9f2721edaad5255b0bc8f268f721289f2752183d541b",
        )
        schedule = runner.expected_schedule(4)
        self.assertEqual(len(schedule), 8)
        self.assertEqual(
            [row["position"] for row in schedule], [0, 1] * 4
        )
        self.assertEqual(schedule[0]["arm"], RTDL_ARM)
        self.assertEqual(schedule[2]["arm"], PYOPTIX_ARM)

    def test_timing_recount_rejects_every_derived_field_drift(self) -> None:
        timing = {
            "sample_count": 4,
            "samples_ns": [11, 17, 13, 19],
            "minimum_ns": 11,
            "median_ns": 15,
            "maximum_ns": 19,
        }
        self.assertEqual(
            runner._validate_timing(timing, 4, "test"),
            timing["samples_ns"],
        )
        for field, replacement in (
            ("sample_count", 3),
            ("minimum_ns", 10),
            ("median_ns", 14),
            ("maximum_ns", 20),
        ):
            with self.subTest(field=field):
                forged = dict(timing)
                forged[field] = replacement
                with self.assertRaisesRegex(RuntimeError, "timing values differ"):
                    runner._validate_timing(forged, 4, "test")

    def test_summary_enforces_setup_and_steady_gates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {}
            for name in (
                "preregistration",
                "cache_preparation",
                "native",
                "native_build_manifest",
                "leaf_cache_manifest",
                "executable_cache_manifest",
                "device_source",
                "pyoptix_build_receipt",
            ):
                path = root / name
                path.write_bytes(name.encode("ascii"))
                paths[name] = path
            args = SimpleNamespace(
                blocks=2,
                warmups=1,
                repetitions=4,
                expected_source_commit="a" * 40,
                preregistration=paths["preregistration"],
                preregistration_value={"preregistration_sha256": "b" * 64},
                cache_preparation=paths["cache_preparation"],
                cache_preparation_value={"preparation_sha256": "c" * 64},
                native=paths["native"],
                native_build_manifest=paths["native_build_manifest"],
                leaf_cache_manifest=paths["leaf_cache_manifest"],
                leaf_cache_manifest_sha256="d" * 64,
                executable_cache_manifest=paths["executable_cache_manifest"],
                executable_cache_manifest_sha256="e" * 64,
                device_source=paths["device_source"],
                pyoptix_build_receipt=paths["pyoptix_build_receipt"],
            )

            def row(arm: str, block: int, setup: int, steady: int):
                samples = [steady] * args.repetitions
                return {
                    "arm": arm,
                    "block": block,
                    "measurements": {
                        "setup_plus_first_ns": setup,
                        "steady_public": {
                            "sample_count": args.repetitions,
                            "samples_ns": samples,
                            "minimum_ns": steady,
                            "median_ns": steady,
                            "maximum_ns": steady,
                        },
                    },
                }

            rows = []
            for block in range(args.blocks):
                rows.extend((
                    row(RTDL_ARM, block, 500_000_000, 366_340),
                    row(PYOPTIX_ARM, block, 500_000_000, 3_500_000),
                ))
            with patch.object(runner, "_git", return_value="f" * 40):
                summary = runner.build_summary(
                    args,
                    rows,
                    runner.expected_schedule(args.blocks),
                    {"compute_capability": "8.9"},
                )
            self.assertTrue(summary["status"].startswith("PASS__"))
            self.assertTrue(all(summary["gates"].values()))

            rows[0]["measurements"]["steady_public"].update({
                "samples_ns": [500_000] * args.repetitions,
                "minimum_ns": 500_000,
                "median_ns": 500_000,
                "maximum_ns": 500_000,
            })
            with patch.object(runner, "_git", return_value="f" * 40):
                adverse = runner.build_summary(
                    args,
                    rows,
                    runner.expected_schedule(args.blocks),
                    {"compute_capability": "8.9"},
                )
            self.assertTrue(adverse["status"].startswith("FAIL__"))
            self.assertFalse(
                adverse["gates"][
                    "worst_worker_rtdl_steady_regression_at_most_1_25"
                ]
            )

    def test_cache_fill_and_sensitivity_claim_boundaries_are_explicit(self) -> None:
        prereg = json.loads(Path(
            "history/internal_docs/goal5846_relation_startup_20260905/"
            "PREREGISTRATION.json"
        ).read_text(encoding="utf-8"))
        self.assertTrue(
            prereg["first_ever_cache_fill_policy"][
                "must_be_excluded_from_registered_estimands"
            ]
        )
        self.assertTrue(
            prereg["known_comparison_boundary"][
                "not_a_universal_aot_deployment_parity_claim"
            ]
        )
        self.assertFalse(
            prereg["claim_boundary"][
                "precompiled_pyoptix_parity_claim_authorized"
            ]
        )


if __name__ == "__main__":
    unittest.main()
