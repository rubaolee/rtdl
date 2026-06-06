from __future__ import annotations

import importlib.util
import os
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

    def test_comparison_rows_disclose_boundary_event_route_is_not_pip_membership(self) -> None:
        rayjoin = {
            "lsi": {
                "query_ms_reported": {"median": 0.2},
                "intersection_counts": {"last": 3},
            },
            "pip": {
                "query_ms_reported": {"median": 0.2},
                "intersection_counts": {"last": None},
            },
        }
        rtdl = {
            "lsi": {
                "prepared_query_ms": {"median": 0.3},
                "counts": {"last": 3},
            },
            "pip": {
                "prepared_query_ms": {"median": 0.1},
                "counts": {"last": 512},
                "count_mode": "boundary_event_point_id_count_device_columns",
            },
        }

        rows = MODULE.build_comparison_rows(rayjoin, rtdl)

        pip = next(row for row in rows if row["workload"] == "pip")
        self.assertEqual(pip["count_contract_status"], "rtdl_boundary_event_count_not_pip_membership")
        self.assertFalse(pip["rayjoin_positive_assignment_count_available"])

    def test_comparison_rows_can_be_lsi_only_for_long_repeated_timing(self) -> None:
        rayjoin = {
            "lsi": {
                "query_ms_reported": {"median": 0.4},
                "intersection_counts": {"last": 4977},
            },
            "pip": {
                "query_ms_reported": {"median": 9.9},
                "intersection_counts": {"last": None},
            },
        }
        rtdl = {
            "lsi": {
                "prepared_query_ms": {"median": 0.22},
                "counts": {"last": 4977},
            },
            "pip": {
                "prepared_query_ms": {"median": 9.9},
                "counts": {"last": 0},
            },
        }

        rows = MODULE.build_comparison_rows(rayjoin, rtdl, workloads=("lsi",))

        self.assertEqual([row["workload"] for row in rows], ["lsi"])
        self.assertEqual(rows[0]["count_contract_status"], "matching_visible_lsi_count")
        self.assertLess(rows[0]["rtdl_over_rayjoin_query_ratio"], 0.6)

    def test_runner_contains_claim_boundary_and_no_release_authorization(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--workloads",
            "long repeated",
            "LSI-only timing",
            "--rtdl-internal-query-repeat",
            "--rayjoin-lsi-poly1",
            "--rayjoin-pip-poly1",
            "--rtdl-pip-point-order",
            "--rtdl-lsi-segment-order",
            "--rtdl-lsi-count-route",
            "--rtdl-pip-scalar-count-pipeline",
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "true_zero_copy_claim_authorized",
            "generic PIP probe ordering",
            "generic locality probe",
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
        self.assertEqual(row["process_wall_ms"]["count"], 1)
        self.assertGreaterEqual(row["process_wall_ms"]["samples"][0], 0.0)

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

    def test_rtdl_lsi_segment_order_passes_through_to_app(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_run(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.0005,
                    "query_segment_order_sec": 0.00003,
                    "static_segment_order_sec": 0.00004,
                    "query_pack_sec": 0.0001,
                    "prepare_static_scene_sec": 0.0002,
                },
                "summary": {"intersection_count": 9},
                "row_count": 9,
                "native_phase_timings": {},
            }

        with mock.patch.object(MODULE.rayjoin_app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            row = MODULE.run_rtdl_samples(
                workload="lsi",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                segment_order_mode="morton_xy",
        )

        self.assertEqual(row["segment_order_mode"], "morton_xy")
        self.assertAlmostEqual(row["query_order_ms"]["samples"][0], 0.03)
        self.assertAlmostEqual(row["static_order_ms"]["samples"][0], 0.04)
        self.assertEqual(calls[0]["kwargs"]["segment_order_mode"], "morton_xy")

    def test_rtdl_lsi_dense_count_route_uses_generic_left_id_count_helper(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_dense(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {"left_id_count_device_columns_sec": 0.00027},
                "summary": {"intersection_count": 269},
                "row_count": 269,
                "prepared_reuse": {"prepare_static_scene_sec": 0.0008},
                "packed_left_reuse": {"pack_seconds": 0.0002},
            }

        with mock.patch.object(
            MODULE.rayjoin_app,
            "run_rayjoin_prepared_optix_left_id_dense_count_workload",
            side_effect=fake_dense,
        ):
            row = MODULE.run_rtdl_samples(
                workload="lsi",
                dataset="fake.cdb + fake2.cdb",
                warmup=0,
                repeat=1,
                lsi_count_route="left_id_dense_count",
            )

        self.assertEqual(row["lsi_count_route"], "left_id_dense_count")
        self.assertEqual(row["prepared_query_ms"]["samples"], [0.27])
        self.assertEqual(row["query_pack_ms"]["samples"], [0.2])
        self.assertEqual(row["prepare_static_scene_ms"]["samples"], [0.8])
        self.assertEqual(row["internal_query_repeat"], 1)
        self.assertEqual(row["internal_warmup"], 0)
        self.assertEqual(row["counts"]["last"], 269)
        self.assertEqual(calls[0]["args"], ("lsi",))
        self.assertEqual(calls[0]["kwargs"]["dataset"], "fake.cdb + fake2.cdb")

    def test_rtdl_lsi_dense_count_route_passes_internal_repeat_to_app_helper(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_dense(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.00023,
                    "prepared_query_sec_total_sec": 2.3,
                    "query_pack_sec": 0.0002,
                    "prepare_static_scene_sec": 0.0008,
                },
                "summary": {"intersection_count": 4977},
                "row_count": 4977,
                "native_phase_timings": {"mode": "left_id_count_device_columns"},
            }

        with mock.patch.object(
            MODULE.rayjoin_app,
            "run_rayjoin_prepared_optix_left_id_dense_count_workload",
            side_effect=fake_dense,
        ):
            row = MODULE.run_rtdl_samples(
                workload="lsi",
                dataset="fake.cdb + fake2.cdb",
                warmup=0,
                repeat=1,
                lsi_count_route="left_id_dense_count",
                internal_query_repeat=10000,
                internal_warmup=20,
            )

        self.assertEqual(row["internal_query_repeat"], 10000)
        self.assertEqual(row["internal_warmup"], 20)
        self.assertEqual(row["prepared_query_total_ms"]["samples"], [2300.0])
        self.assertEqual(calls[0]["kwargs"]["query_repeat"], 10000)
        self.assertEqual(calls[0]["kwargs"]["warmup"], 20)
        self.assertEqual(row["counts"]["last"], 4977)

    def test_rtdl_pip_scalar_count_pipeline_is_scoped_and_recorded(self) -> None:
        observed_env: list[str | None] = []

        def fake_run(*args, **kwargs):
            observed_env.append(os.environ.get("RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE"))
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.00033,
                    "validation_exact_query_sec": 0.00065,
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
                warmup=0,
                repeat=1,
                count_mode="device_filtered_validated",
                query_axis="z_point",
                boundary_mode="inclusive",
                pip_scalar_count_pipeline=True,
            )

        self.assertEqual(observed_env, ["1"])
        self.assertTrue(row["pip_scalar_count_pipeline"])
        self.assertEqual(row["query_axis"], "z_point")
        self.assertEqual(row["device_filtered_boundary_mode"], "inclusive")

    def test_rtdl_pip_boundary_event_count_route_discloses_non_membership_contract(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_run(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.00021,
                    "boundary_event_device_columns_sec": 0.00018,
                    "boundary_event_grouped_count_sec": 0.00003,
                    "query_pack_sec": 0.0001,
                    "prepare_static_scene_sec": 0.0002,
                },
                "summary": {
                    "boundary_event_row_count": 512,
                    "boundary_event_contract_not_positive_membership": True,
                    "output_contract": "point_closed_shape_first_boundary_event_count_by_point_id_device_columns",
                },
                "row_count": 512,
                "native_phase_timings": {"mode": "boundary_event_device_columns"},
            }

        with mock.patch.object(MODULE.rayjoin_app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            row = MODULE.run_rtdl_samples(
                workload="pip",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                count_mode="boundary_event_point_id_count_device_columns",
        )

        self.assertEqual(row["count_mode"], "boundary_event_point_id_count_device_columns")
        self.assertAlmostEqual(row["prepared_query_ms"]["samples"][0], 0.21)
        self.assertAlmostEqual(row["boundary_event_device_columns_ms"]["samples"][0], 0.18)
        self.assertAlmostEqual(row["boundary_event_grouped_count_ms"]["samples"][0], 0.03)
        self.assertEqual(row["validation_exact_query_ms"]["samples"], [])
        self.assertEqual(row["counts"]["last"], 512)
        self.assertIsNone(row["device_filtered_boundary_mode"])
        self.assertEqual(calls[0]["kwargs"]["count_mode"], "boundary_event_point_id_count_device_columns")

    def test_rtdl_pip_boundary_event_count_route_rejects_missing_disclosure_even_in_warmup(self) -> None:
        def fake_run(*_args, **_kwargs):
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.00021,
                    "query_pack_sec": 0.0001,
                    "prepare_static_scene_sec": 0.0002,
                },
                "summary": {
                    "boundary_event_row_count": 512,
                    "output_contract": "point_closed_shape_first_boundary_event_count_by_point_id_device_columns",
                },
                "row_count": 512,
                "native_phase_timings": {"mode": "boundary_event_device_columns"},
            }

        with mock.patch.object(MODULE.rayjoin_app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            with self.assertRaisesRegex(RuntimeError, "did not disclose non-membership contract"):
                MODULE.run_rtdl_samples(
                    workload="pip",
                    dataset="fake.cdb",
                    warmup=1,
                    repeat=1,
                    count_mode="boundary_event_point_id_count_device_columns",
                )

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

    def test_rtdl_non_lsi_rejects_segment_order_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "segment_order_mode is only supported"):
            MODULE.run_rtdl_samples(
                workload="pip",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                segment_order_mode="morton_xy",
            )

    def test_rtdl_lsi_dense_count_route_rejects_segment_ordering(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires natural LSI segment order"):
            MODULE.run_rtdl_samples(
                workload="lsi",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                lsi_count_route="left_id_dense_count",
                segment_order_mode="morton_xy",
            )

    def test_rtdl_internal_repeat_rejects_non_lsi_dense_route(self) -> None:
        with self.assertRaisesRegex(ValueError, "internal query repeat"):
            MODULE.run_rtdl_samples(
                workload="pip",
                dataset="fake.cdb",
                warmup=0,
                repeat=1,
                internal_query_repeat=2,
            )


if __name__ == "__main__":
    unittest.main()
