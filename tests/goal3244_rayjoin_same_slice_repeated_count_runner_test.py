from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
SPEC = importlib.util.spec_from_file_location("goal3244_runner", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class subprocess_completed:
    def __init__(self, *, stdout: str, stderr: str, returncode: int) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class Goal3244RayJoinSameSliceRepeatedCountRunnerTest(unittest.TestCase):
    def test_parse_rayjoin_lsi_log_extracts_count_and_timings(self) -> None:
        parsed = MODULE.parse_rayjoin_query_log(
            """
I20260604 run_query.cu:301] Iter: 4
I20260604 run_query.cu:306] Intersections: 269 Queue Load Factor: 0.0501678
Timing results:
 - Build Index: 0.428915 ms
 - Warmup: 1.20902 ms
 - Query: 0.229406 ms
"""
        )

        self.assertEqual(parsed["intersections"], 269)
        self.assertEqual(parsed["build_index_ms"], 0.428915)
        self.assertEqual(parsed["warmup_ms"], 1.20902)
        self.assertEqual(parsed["query_ms"], 0.229406)
        self.assertFalse(parsed["positive_assignment_count_available"])

    def test_parse_rayjoin_pip_log_tracks_checker_without_count(self) -> None:
        parsed = MODULE.parse_rayjoin_query_log(
            """
I20260604 rt_engine.cu:554] optixLaunch, [w,h,d] = 25392,1,1
I20260604 run_query.cu:97] Map: 0 passed check
Timing results:
 - Warmup: 1.00303 ms
 - Query: 0.185776 ms
"""
        )

        self.assertIsNone(parsed["intersections"])
        self.assertTrue(parsed["checker_passed"])
        self.assertEqual(parsed["optix_launch_widths"], [25392])
        self.assertFalse(parsed["positive_assignment_count_available"])

    def test_comparison_rows_keep_pip_boundary_and_lsi_count_contract(self) -> None:
        rayjoin = {
            "lsi": {
                "query_ms_reported": {"median": 0.229406},
                "intersection_counts": {"last": 269},
            },
            "pip": {
                "query_ms_reported": {"median": 0.185776},
                "intersection_counts": {"last": None},
            },
        }
        rtdl = {
            "lsi": {
                "prepared_query_ms": {"median": 1.537322998046875},
                "counts": {"last": 269},
            },
            "pip": {
                "prepared_query_ms": {"median": 1.268438994884491},
                "counts": {"last": 1430},
            },
        }

        rows = MODULE.build_comparison_rows(rayjoin, rtdl)

        lsi = next(row for row in rows if row["workload"] == "lsi")
        pip = next(row for row in rows if row["workload"] == "pip")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertGreater(lsi["rtdl_over_rayjoin_query_ratio"], 6.7)
        self.assertLess(lsi["rtdl_over_rayjoin_query_ratio"], 6.8)
        self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertIsNone(pip["rayjoin_visible_count"])
        self.assertFalse(pip["rayjoin_positive_assignment_count_available"])

    def test_runner_contains_claim_boundary_and_no_release_authorization(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--rayjoin-lsi-poly1",
            "--rayjoin-pip-poly1",
            "--rtdl-pip-point-order",
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "true_zero_copy_claim_authorized",
            "generic PIP probe ordering",
            "RayJoin query_exec PIP still does not expose positive assignment count",
            "does not divide it by repeat",
        ):
            self.assertIn(phrase, text)
        self.assertTrue(all(value is False for value in MODULE.CLAIM_BOUNDARY.values()))

    def test_rayjoin_process_samples_accepts_explicit_input_overrides(self) -> None:
        completed = subprocess_completed(
            stdout="""
Timing results:
 - Build Index: 0.4 ms
 - Warmup: 0.5 ms
 - Query: 0.6 ms
""",
            stderr="",
            returncode=0,
        )
        with tempfile.TemporaryDirectory() as tmp_dir, mock.patch.object(
            MODULE.subprocess,
            "run",
            return_value=completed,
        ) as run_mock:
            row = MODULE.run_rayjoin_process_samples(
                query_exec=Path("/bin/query_exec"),
                workload="pip",
                data_dir=PurePosixPath("/data"),
                poly1_override=PurePosixPath("/data/custom_poly1.cdb"),
                poly2_override=PurePosixPath("/data/custom_poly2.cdb"),
                warmup=1,
                repeat=2,
                process_repeats=1,
                timeout_seconds=30,
                log_dir=Path(tmp_dir),
            )

        command = run_mock.call_args.args[0]
        self.assertIn("-poly1=/data/custom_poly1.cdb", command)
        self.assertIn("-poly2=/data/custom_poly2.cdb", command)
        self.assertEqual(row["input_poly1"], "/data/custom_poly1.cdb")
        self.assertEqual(row["input_poly2"], "/data/custom_poly2.cdb")

    def test_rayjoin_process_samples_requires_both_override_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires both poly1 and poly2"):
            MODULE.run_rayjoin_process_samples(
                query_exec=Path("/bin/query_exec"),
                workload="lsi",
                data_dir=PurePosixPath("/data"),
                poly1_override=PurePosixPath("/data/custom_poly1.cdb"),
                poly2_override=None,
                warmup=1,
                repeat=1,
                process_repeats=1,
                timeout_seconds=30,
                log_dir=ROOT / "scratch",
            )

    def test_rtdl_pip_device_filtered_mode_records_validation_lane(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_run(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.0007,
                    "validation_exact_query_sec": 0.0009,
                    "query_pack_sec": 0.0001,
                    "prepare_static_scene_sec": 0.0002,
                },
                "summary": {
                    "positive_assignment_count": 1430,
                    "device_filtered_count_matches_exact": True,
                },
                "row_count": 1430,
                "native_phase_timings": {"mode": "device_filtered_count"},
            }

        with mock.patch.object(MODULE.rayjoin_app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            row = MODULE.run_rtdl_samples(
                workload="pip",
                dataset="fake.cdb",
                warmup=1,
                repeat=2,
                count_mode="device_filtered_validated",
            )

        self.assertEqual(row["count_mode"], "device_filtered_validated")
        self.assertEqual(row["prepared_query_ms"]["samples"], [0.7, 0.7])
        self.assertEqual(row["validation_exact_query_ms"]["samples"], [0.9, 0.9])
        self.assertEqual(row["counts"]["last"], 1430)
        self.assertEqual(row["point_order_mode"], "natural")
        self.assertEqual(row["native_phase_samples"], [{"mode": "device_filtered_count"}] * 2)
        self.assertTrue(all(call["kwargs"]["count_mode"] == "device_filtered_validated" for call in calls))

    def test_rtdl_pip_point_order_passes_through_to_app(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_run(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.0005,
                    "query_pack_sec": 0.0001,
                    "prepare_static_scene_sec": 0.0002,
                },
                "summary": {"positive_assignment_count": 7},
                "row_count": 7,
                "native_phase_timings": {},
            }

        with mock.patch.object(MODULE.rayjoin_app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            row = MODULE.run_rtdl_samples(
                workload="pip",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                point_order_mode="morton_xy",
            )

        self.assertEqual(row["point_order_mode"], "morton_xy")
        self.assertEqual(calls[0]["kwargs"]["point_order_mode"], "morton_xy")

    def test_rtdl_non_pip_rejects_device_filtered_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "only supported for RTDL PIP"):
            MODULE.run_rtdl_samples(
                workload="lsi",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                count_mode="device_filtered_validated",
            )

    def test_rtdl_non_pip_rejects_point_order_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "point_order_mode is only supported"):
            MODULE.run_rtdl_samples(
                workload="lsi",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                point_order_mode="morton_xy",
            )


if __name__ == "__main__":
    unittest.main()
