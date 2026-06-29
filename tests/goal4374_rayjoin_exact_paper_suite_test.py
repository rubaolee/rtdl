from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal4374RayjoinExactPaperSuiteTest(unittest.TestCase):
    def test_exact_suite_defines_eight_pairs_three_programs_and_no_analogues(self) -> None:
        from rtdsl.rayjoin_paper_suite import exact_suite_manifest
        from rtdsl.rayjoin_paper_suite import paper_cases
        from rtdsl.rayjoin_paper_suite import paper_pairs
        from rtdsl.rayjoin_paper_suite import paper_programs

        self.assertEqual(len(paper_pairs()), 8)
        self.assertEqual(len(paper_programs()), 3)
        self.assertEqual(len(paper_cases()), 24)

        payload = exact_suite_manifest(ROOT / "missing_exact_rayjoin_dataset_root")
        self.assertFalse(payload["definition"]["analogue_inputs_count_as_exact"])
        self.assertFalse(payload["definition"]["overlay_seed_counts_as_overlay"])
        self.assertEqual(payload["definition"]["default_grid_size"], 15000)
        self.assertEqual(payload["definition"]["default_xsect_factor"], "0.1")
        self.assertEqual(payload["definition"]["default_enlarge"], "3.5")
        self.assertIn("same_source_regenerated_cdb", payload["definition"]["input_provenance_modes"])

    def test_section57_table4_defines_full_eight_pair_overlay_reference(self) -> None:
        from rtdsl.rayjoin_paper_suite import RAYJOIN_SECTION57_TABLE4_SECONDS
        from rtdsl.rayjoin_paper_suite import paper_pairs

        pair_ids = {pair.pair_id for pair in paper_pairs()}
        self.assertEqual(len(pair_ids), 8)
        for artifact, by_pair in RAYJOIN_SECTION57_TABLE4_SECONDS.items():
            self.assertEqual(set(by_pair), pair_ids, artifact)

        self.assertEqual(RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"]["county_zipcode"], (0.12, 0.07))
        self.assertEqual(RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"]["block_water"], (0.23, 0.12))
        self.assertEqual(RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"]["lkna_pkna"], (0.25, 0.21))
        self.assertEqual(RAYJOIN_SECTION57_TABLE4_SECONDS["LBVH*"]["lkeu_pkeu"], (None, None))

    def test_dataset_paths_match_rayjoin_paper_script_layout(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs

        paths = {(pair.pair_id, pair.left_relative_path, pair.right_relative_path) for pair in paper_pairs()}
        self.assertIn(
            (
                "county_zipcode",
                "point_cdb/dtl_cnty/dtl_cnty_Point.cdb",
                "point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb",
            ),
            paths,
        )
        self.assertIn(
            (
                "lkna_pkna",
                "point_cdb/lakes/North_America/lakes_North_America_Point.cdb",
                "point_cdb/parks/North_America/parks_North_America_Point.cdb",
            ),
            paths,
        )

    def test_overlay_is_marked_as_exact_compute_with_optional_output(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_programs

        by_id = {program.program_id: program for program in paper_programs()}
        self.assertEqual(by_id["lsi"].rtdl_status, "implemented")
        self.assertEqual(by_id["pip"].rtdl_status, "implemented")
        self.assertIn("every point returned by S.get_points()", by_id["pip"].input_contract)
        self.assertEqual(by_id["overlay"].rtdl_status, "implemented_compute_optional_output")
        self.assertIn("optional output-chain assembly", by_id["overlay"].output_contract)
        self.assertIn("RTDL overlay_seed rows still do not count", by_id["overlay"].gap_note)

    def test_paper_pip_helper_uses_all_query_cdb_points(self) -> None:
        from rtdsl.datasets import CdbChain
        from rtdsl.datasets import CdbDataset
        from rtdsl.datasets import CdbPoint
        from rtdsl.datasets import chains_to_all_points
        from rtdsl.datasets import chains_to_probe_points

        dataset = CdbDataset(
            name="two_chains",
            chains=(
                CdbChain(1, 3, 1, 3, 10, 0, (CdbPoint(0, 0), CdbPoint(1, 0), CdbPoint(1, 1))),
                CdbChain(2, 2, 4, 5, 20, 0, (CdbPoint(2, 0), CdbPoint(2, 1))),
            ),
        )
        self.assertEqual(len(chains_to_probe_points(dataset)), 2)
        all_points = chains_to_all_points(dataset)
        self.assertEqual(len(all_points), 5)
        self.assertEqual(tuple(point.id for point in all_points), (1, 2, 3, 4, 5))

    def test_author_command_uses_paper_parameters_and_query_exec_for_lsi_pip(self) -> None:
        from rtdsl.rayjoin_paper_suite import build_rayjoin_author_command
        from rtdsl.rayjoin_paper_suite import paper_cases

        case = next(case for case in paper_cases() if case.case_id == "pip_county_zipcode")
        command = build_rayjoin_author_command(
            case,
            dataset_root="/datasets",
            query_exec="/rayjoin/release/bin/query_exec",
            polyover_exec="/rayjoin/release/bin/polyover_exec",
        ).command
        self.assertEqual(command[0], "/rayjoin/release/bin/query_exec")
        self.assertIn("-query=pip", command)
        self.assertIn("-grid_size=15000", command)
        self.assertIn("-xsect_factor", command)
        self.assertIn("0.1", command)
        self.assertIn("-enlarge=3.5", command)
        self.assertIn("/datasets/point_cdb/dtl_cnty/dtl_cnty_Point.cdb", command)

    def test_remote_posix_paths_survive_windows_command_generation(self) -> None:
        from rtdsl.rayjoin_paper_suite import availability_matrix
        from rtdsl.rayjoin_paper_suite import build_rayjoin_author_command
        from rtdsl.rayjoin_paper_suite import paper_cases

        case = next(case for case in paper_cases() if case.case_id == "lsi_county_zipcode")
        command = build_rayjoin_author_command(
            case,
            dataset_root=Path("/workspace/rayjoin_datasets"),
            query_exec=Path("/workspace/RayJoin_fresh/release/bin/query_exec"),
            polyover_exec=Path("/workspace/RayJoin_fresh/release/bin/polyover_exec"),
        ).command
        self.assertEqual(command[0], "/workspace/RayJoin_fresh/release/bin/query_exec")
        self.assertIn("/workspace/rayjoin_datasets/point_cdb/dtl_cnty/dtl_cnty_Point.cdb", command)

        row = availability_matrix(
            Path("/workspace/rayjoin_datasets"),
            pair_ids=("county_zipcode",),
            program_ids=("lsi",),
        )[0]
        self.assertEqual(
            row.left.path,
            "/workspace/rayjoin_datasets/point_cdb/dtl_cnty/dtl_cnty_Point.cdb",
        )

    def test_availability_blocks_missing_exact_inputs(self) -> None:
        from rtdsl.rayjoin_paper_suite import availability_matrix

        with tempfile.TemporaryDirectory() as tmp:
            rows = availability_matrix(tmp, pair_ids=("county_zipcode",), program_ids=("lsi",))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertFalse(row.exact_input_ready)
        self.assertIsNotNone(row.blocker)
        self.assertIn("missing exact CDB input", row.blocker or "")

    def test_overlay_compute_optional_output_status_is_runnable_when_inputs_exist(self) -> None:
        from rtdsl.rayjoin_paper_suite import availability_matrix
        from rtdsl.rayjoin_paper_suite import paper_pairs

        pair = next(pair for pair in paper_pairs() if pair.pair_id == "county_zipcode")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / pair.left_relative_path
            right = root / pair.right_relative_path
            left.parent.mkdir(parents=True, exist_ok=True)
            right.parent.mkdir(parents=True, exist_ok=True)
            left.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            right.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            row = availability_matrix(root, pair_ids=("county_zipcode",), program_ids=("overlay",))[0]

        self.assertTrue(row.exact_input_ready)
        self.assertEqual(row.rtdl_status, "implemented_compute_optional_output")
        self.assertIsNone(row.blocker)

    def test_section57_overlay_matrix_script_plans_all_eight_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "out"
            plan_json = output_dir / "section57_plan.json"
            plan_md = output_dir / "section57_plan.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "rayjoin_section57_overlay_matrix.py"),
                    "plan",
                    "--dataset-root",
                    str(root / "missing_dataset"),
                    "--output-dir",
                    str(output_dir),
                    "--query-exec",
                    "/rayjoin/release/bin/query_exec",
                    "--polyover-exec",
                    "/rayjoin/release/bin/polyover_exec",
                    "--output-json",
                    str(plan_json),
                    "--output-md",
                    str(plan_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            self.assertEqual(completed.stdout, "")
            payload = json.loads(plan_json.read_text(encoding="utf-8"))
            markdown = plan_md.read_text(encoding="utf-8")

        self.assertEqual(payload["coverage"]["overlay_pairs_total"], 8)
        self.assertEqual(len(payload["rows"]), 8)
        self.assertIn("RayJoin Section 5.7 Overlay 8/8 Execution Plan", markdown)
        self.assertEqual(
            {row["pair_id"] for row in payload["rows"]},
            {
                "county_zipcode",
                "block_water",
                "lkaf_pkaf",
                "lkas_pkas",
                "lkau_pkau",
                "lkeu_pkeu",
                "lkna_pkna",
                "lksa_pksa",
            },
        )
        first_row = payload["rows"][0]
        self.assertIn("RayJoin*", first_row["paper_table4_seconds"])
        self.assertIn("rtdl_optix", first_row["commands"])
        self.assertIn("--backend", first_row["commands"]["rtdl_optix"])
        self.assertIn("optix", first_row["commands"]["rtdl_optix"])
        self.assertIn("embree", first_row["commands"]["rtdl_embree"])
        self.assertIn("v4_numba", first_row["commands"])
        self.assertIn("--section57-auto-numba", first_row["commands"]["v4_numba"])
        self.assertIn("--pairs", first_row["commands"]["v4_numba"])
        self.assertIn("county_zipcode", first_row["commands"]["v4_numba"])

    def test_section57_overlay_matrix_runner_records_timeout_without_crashing(self) -> None:
        script_path = ROOT / "scripts" / "rayjoin_section57_overlay_matrix.py"
        spec = importlib.util.spec_from_file_location("rayjoin_section57_overlay_matrix", script_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None
        assert spec.loader is not None
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "timeout.json"
            result = module._run_one(
                [sys.executable, "-c", "import time; time.sleep(2)"],
                output_json=output_json,
                timeout_sec=1,
            )

        self.assertFalse(result["completed"])
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["exit_code"])
        self.assertEqual(result["timeout_sec"], 1)

    def test_section57_author_repeated_payload_keeps_median_as_author_total(self) -> None:
        script_path = ROOT / "scripts" / "rayjoin_section57_overlay_matrix.py"
        spec = importlib.util.spec_from_file_location("rayjoin_section57_overlay_matrix", script_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None
        assert spec.loader is not None
        spec.loader.exec_module(module)

        command = ["runner", "--output-json", "old.json", "--flag"]
        updated = module._command_with_output_json(command, Path("new.json"))
        self.assertEqual(updated, ["runner", "--output-json", "new.json", "--flag"])
        self.assertEqual(command, ["runner", "--output-json", "old.json", "--flag"])
        self.assertEqual(module._extract_author_total({"elapsed_sec": 5.5, "hot_median_sec": 5.5}), 5.5)

    def test_contract_doc_forbids_seed_overlay_claim(self) -> None:
        doc = (
            ROOT
            / "docs"
            / "research"
            / "rayjoin"
            / "rayjoin_exact_paper_reproduction_contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("RTDL `overlay_seed` rows do not count as polygon overlay", doc)
        self.assertIn("Analogue, fixture-subset, or synthetic inputs do not count as exact paper reproduction", doc)
        self.assertIn("all points from query map S", doc)
        self.assertIn("RTDL is a general language/runtime system", doc)
        self.assertIn("must separate end-to-end time from app ingestion", doc)
        self.assertIn(".rtdl_rayjoin_overlay_packed_cache", doc)

    def test_rtdl_performance_principles_define_no_unnecessary_overhead_contract(self) -> None:
        doc = (ROOT / "docs" / "research" / "rtdl_performance_principles.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("not a hand-specialized rewrite", doc)
        self.assertIn("does not promise to beat", doc)
        self.assertIn("avoid unnecessary data movement", doc)
        self.assertIn("Partner Boundary", doc)
        self.assertIn("Unknown gap", doc)

    def test_rtdl_runner_uses_paper_pip_stream_and_runs_overlay(self) -> None:
        script = (ROOT / "scripts" / "rayjoin_paper_reproduction_suite.py").read_text(encoding="utf-8")
        self.assertIn("run-rtdl", script)
        self.assertIn("from rtdsl.rayjoin_overlay import _run_lsi_rows", script)
        self.assertIn("rayjoin_overlay_lsi_rows", script)
        self.assertIn("_packed_cache_partner_env", script)
        self.assertIn(".rtdl_rayjoin_overlay_packed_cache", script)
        self.assertIn("--disable-packed-cache", script)
        self.assertIn('"partner_cache": packed_cache', script)
        self.assertIn("rayjoin_author_lsi_intersect_test_endpoint_collinear_contract", script)
        self.assertIn("load_cdb_overlay_packed_inputs", script)
        self.assertIn("_summarize_overlay_backend_runs", script)
        self.assertIn("total_median_sec", script)
        self.assertIn("phase_median_seconds", script)
        self.assertIn("scale_bounds = _shared_rayjoin_bounds(base_inputs, query_inputs)", script)
        self.assertIn("with _rayjoin_cdb_point_location_env(1, scale_bounds):", script)
        self.assertIn("packed_query_points = query_inputs.points", script)
        self.assertIn("prepare_directed_segment_point_location_2d_optix", script)
        self.assertIn("prepare_directed_segment_point_location_2d_embree", script)
        self.assertIn("prepared.prepare_query_points(packed_query_points)", script)
        self.assertIn("count_positive_faces_device_points(prepared_points)", script)
        self.assertIn("write_segment_ids_device_points(prepared_points)", script)
        self.assertIn("author_shape_device_resident_closest_segment_id_column", script)
        self.assertIn("run_rayjoin_overlay_rtdl", script)
        self.assertIn("--assemble-overlay-output", script)

    def test_overlay_output_chain_writer_is_not_legacy_seed(self) -> None:
        from rtdsl.datasets import CdbChain
        from rtdsl.datasets import CdbDataset
        from rtdsl.datasets import CdbPoint
        from rtdsl.rayjoin_overlay import RayjoinOverlayIntersection
        from rtdsl.rayjoin_overlay import _assemble_output_chains

        left = CdbDataset(
            name="left",
            chains=(
                CdbChain(
                    1,
                    2,
                    1,
                    2,
                    10,
                    0,
                    (CdbPoint(0.0, 0.0), CdbPoint(2.0, 0.0)),
                ),
            ),
        )
        right = CdbDataset(
            name="right",
            chains=(
                CdbChain(
                    1,
                    2,
                    1,
                    2,
                    20,
                    0,
                    (CdbPoint(1.0, -1.0), CdbPoint(1.0, 1.0)),
                ),
            ),
        )
        xsect = RayjoinOverlayIntersection(eid0=0, eid1=0, x=1.0, y=0.0)
        chains, face_count = _assemble_output_chains(
            (left, right),
            ([xsect], [xsect]),
            ((20, 20), (10, 10)),
        )
        self.assertGreaterEqual(len(chains), 2)
        self.assertEqual(face_count, 1)
        self.assertTrue(any(chain.left_polygon_id == 1 for chain in chains))

    def test_overlay_no_output_uses_face_id_device_column_classification(self) -> None:
        import numpy as np
        import rtdsl.rayjoin_overlay as overlay

        class FakeRunner:
            instances = []

            def __init__(self, backend, base_segments, *, query_map_id, scale_bounds):
                self.backend = backend
                self.query_map_id = int(query_map_id)
                self.count_calls = []
                self.face_calls = []
                self.prepare_sec = 0.01

            def __enter__(self):
                FakeRunner.instances.append(self)
                return self

            def __exit__(self, exc_type, exc, tb):
                return None

            def count(self, points):
                self.count_calls.append(int(points.count))
                positive_count = 100 + self.query_map_id + len(self.count_calls)
                return positive_count, {
                    "mode": "count",
                    "point_count": int(points.count),
                    "positive_face_count": positive_count,
                }

            def classify(self, points):
                return None, {
                    "mode": "face_ids_device_points",
                    "point_count": int(points.count),
                    "face_id_output_count": int(points.count),
                    "output_contract": (
                        "directed_segment_point_location_face_id_device_column_no_host_download_no_positive_count_atomic"
                    ),
                }

            def faces(self, points, point_count):
                self.face_calls.append(int(point_count))
                return np.zeros(point_count, dtype=np.uint32), {"mode": "rows"}

        left_points = SimpleNamespace(count=4)
        right_points = SimpleNamespace(count=3)
        left_inputs = overlay.RayjoinOverlayPackedInputs(
            name="left",
            segments=SimpleNamespace(count=1),
            cdb_segments=object(),
            points=left_points,
            segment_coords=(object(), object(), object(), object()),
            point_coords=(np.array([0.0, 2.0]), np.array([0.0, 2.0])),
            edge_starts=(np.array([0.0]), np.array([0.0])),
            chain_count=1,
            edge_count=1,
            point_count=4,
        )
        right_inputs = overlay.RayjoinOverlayPackedInputs(
            name="right",
            segments=SimpleNamespace(count=1),
            cdb_segments=object(),
            points=right_points,
            segment_coords=(object(), object(), object(), object()),
            point_coords=(np.array([0.0, 2.0]), np.array([0.0, 2.0])),
            edge_starts=(np.array([0.0]), np.array([0.0])),
            chain_count=1,
            edge_count=1,
            point_count=3,
        )
        lsi_rows = np.array(
            [
                (1, 1, 0.5, 0.5),
                (1, 1, 1.5, 1.5),
            ],
            dtype=[
                ("left_id", np.uint32),
                ("right_id", np.uint32),
                ("intersection_point_x", np.float64),
                ("intersection_point_y", np.float64),
            ],
        )
        old_runner = overlay._PreparedPointLocationRunner
        old_lsi_rows = overlay._run_lsi_rows
        try:
            overlay._PreparedPointLocationRunner = FakeRunner
            overlay._run_lsi_rows = lambda *args, **kwargs: (lsi_rows, {"hot_call_sec": 0.0})

            result = overlay._run_rayjoin_overlay_packed(
                left_inputs,
                right_inputs,
                backend="optix",
                assemble_output=False,
            )
        finally:
            overlay._PreparedPointLocationRunner = old_runner
            overlay._run_lsi_rows = old_lsi_rows

        self.assertEqual(len(FakeRunner.instances), 2)
        runners_by_query_map = {runner.query_map_id: runner for runner in FakeRunner.instances}
        self.assertEqual(runners_by_query_map[0].count_calls, [])
        self.assertEqual(runners_by_query_map[1].count_calls, [])
        self.assertEqual(runners_by_query_map[0].face_calls, [])
        self.assertEqual(runners_by_query_map[1].face_calls, [])
        self.assertIsNone(result["vertex_pip"]["map0_positive_faces"])
        self.assertIsNone(result["vertex_pip"]["map1_positive_faces"])
        self.assertIsNone(result["midpoint_pip"]["map0_positive_faces"])
        self.assertIsNone(result["midpoint_pip"]["map1_positive_faces"])
        self.assertEqual(result["midpoint_pip"]["map0_nonfinite_midpoints_dropped"], 0)
        self.assertEqual(result["midpoint_pip"]["map1_nonfinite_midpoints_dropped"], 0)
        self.assertEqual(result["native_timings"]["vertex_pip_map0_in_map1"]["mode"], "face_ids_device_points")
        self.assertIn("no_positive_count_atomic", result["native_timings"]["vertex_pip_map0_in_map1"]["output_contract"])
        self.assertIn("point_location_prepare_wall_sec", result["phase_seconds"])
        self.assertFalse(result["output"]["assembled"])

    def test_lsi_midpoint_projection_drops_nonfinite_points_with_telemetry(self) -> None:
        import numpy as np
        import rtdsl.rayjoin_overlay as overlay

        lsi_rows = np.array(
            [
                (1, 1, 0.0, 0.0),
                (1, 2, 2.0, 0.0),
                (2, 1, np.nan, 0.0),
                (2, 2, 2.0, 0.0),
            ],
            dtype=[
                ("left_id", np.uint32),
                ("right_id", np.uint32),
                ("intersection_point_x", np.float64),
                ("intersection_point_y", np.float64),
            ],
        )
        stats: dict[str, int] = {}

        packed = overlay._midpoint_points_from_lsi_rows_numpy(
            lsi_rows,
            (np.array([0.0, 0.0]), np.array([0.0, 0.0])),
            0,
            stats=stats,
        )

        self.assertEqual(packed.count, 1)
        self.assertEqual(stats["map0_nonfinite_midpoints_dropped"], 1)
        self.assertTrue(np.all(np.isfinite(packed.owner["x"])))
        self.assertTrue(np.all(np.isfinite(packed.owner["y"])))

    def test_large_point_location_stream_auto_uses_generic_adaptive_grouping(self) -> None:
        from rtdsl.rayjoin_overlay import _directed_segment_point_location_grouping_env

        keys = (
            "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE",
            "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE",
            "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE",
            "RTDL_RAYJOIN_CDB_GROUP_MODE",
            "RTDL_RAYJOIN_CDB_GROUP_MAX_SIZE",
            "RTDL_RAYJOIN_CDB_GROUP_AREA_ENLARGE",
        )
        old = {key: os.environ.pop(key, None) for key in keys}
        try:
            with _directed_segment_point_location_grouping_env("optix", (56_000_000, 44_000_000)):
                self.assertEqual(os.environ["RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE"], "adaptive")
                self.assertEqual(os.environ["RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE"], "16")
                self.assertEqual(os.environ["RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE"], "1.2")
            self.assertNotIn("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE", os.environ)

            with _directed_segment_point_location_grouping_env("optix", (17_000_000, 5_000_000)):
                self.assertNotIn("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE", os.environ)

            os.environ["RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE"] = "fixed8"
            with _directed_segment_point_location_grouping_env("optix", (56_000_000, 44_000_000)):
                self.assertEqual(os.environ["RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE"], "fixed8")
        finally:
            for key in keys:
                os.environ.pop(key, None)
                if old[key] is not None:
                    os.environ[key] = old[key]

    def test_overlay_lsi_binary_u64_pair_dump_reader(self) -> None:
        import numpy as np
        from rtdsl.rayjoin_overlay import _rows_from_segment_pair_ids

        with tempfile.TemporaryDirectory() as tmp:
            pair_path = Path(tmp) / "pairs.bin"
            encoded = np.array([(np.uint64(1) << np.uint64(32)) | np.uint64(1)], dtype=np.uint64)
            encoded.tofile(pair_path)
            rows = _rows_from_segment_pair_ids(
                pair_path,
                None,
                None,
                left_coords=(
                    np.array([0.0], dtype=np.float64),
                    np.array([0.0], dtype=np.float64),
                    np.array([2.0], dtype=np.float64),
                    np.array([0.0], dtype=np.float64),
                ),
                right_coords=(
                    np.array([1.0], dtype=np.float64),
                    np.array([-1.0], dtype=np.float64),
                    np.array([1.0], dtype=np.float64),
                    np.array([1.0], dtype=np.float64),
                ),
                binary_u64_pairs=True,
            )

        self.assertEqual(len(rows), 1)
        self.assertEqual(int(rows["left_id"][0]), 1)
        self.assertEqual(int(rows["right_id"][0]), 1)
        self.assertAlmostEqual(float(rows["intersection_point_x"][0]), 1.0)
        self.assertAlmostEqual(float(rows["intersection_point_y"][0]), 0.0)

    def test_embree_rayjoin_lsi_defaults_aabb_scene_build_quality_low(self) -> None:
        from rtdsl.rayjoin_overlay import _rayjoin_lsi_predicate_env

        old_quality = os.environ.pop("RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY", None)
        old_predicate = os.environ.pop("RTDL_EMBREE_SEGMENT_PAIR_PREDICATE", None)
        try:
            with _rayjoin_lsi_predicate_env("embree"):
                self.assertEqual(os.environ["RTDL_EMBREE_SEGMENT_PAIR_PREDICATE"], "rayjoin_lsi")
                self.assertEqual(os.environ["RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY"], "low")
            self.assertNotIn("RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY", os.environ)
            os.environ["RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY"] = "high"
            with _rayjoin_lsi_predicate_env("embree"):
                self.assertEqual(os.environ["RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY"], "high")
            self.assertEqual(os.environ["RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY"], "high")
        finally:
            os.environ.pop("RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY", None)
            os.environ.pop("RTDL_EMBREE_SEGMENT_PAIR_PREDICATE", None)
            if old_quality is not None:
                os.environ["RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY"] = old_quality
            if old_predicate is not None:
                os.environ["RTDL_EMBREE_SEGMENT_PAIR_PREDICATE"] = old_predicate

    def test_native_optix_has_opt_in_rayjoin_lsi_predicate(self) -> None:
        native = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", native)
        self.assertIn("RayjoinLsiScaledSegment", native)
        self.assertIn("__int128", native)
        self.assertIn("rayjoin_lsi_intersection_device", native)
        self.assertIn("rayjoin_lsi_intersection_host", native)
        self.assertIn("params.predicate_mode == 1u", native)
        self.assertIn("params.predicate_mode == 1u ? 1.0f", native)
        self.assertIn("x0 > x1", native)
        self.assertIn("std::fma(x, scale.rx, scale.deltax)", native)
        self.assertIn("std::fma(y, scale.ry, scale.deltay)", native)
        self.assertIn("RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH", native)
        self.assertIn("prepared_left->rayjoin_lsi_scale_key.valid", native)

    def test_native_embree_has_opt_in_rayjoin_lsi_predicate(self) -> None:
        geometry = (ROOT / "src" / "native" / "embree" / "rtdl_embree_geometry.cpp").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp").read_text(
            encoding="utf-8"
        )
        scene = (ROOT / "src" / "native" / "embree" / "rtdl_embree_scene.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("RTDL_EMBREE_SEGMENT_PAIR_PREDICATE", geometry)
        self.assertIn("rayjoin_lsi_segment_intersection", geometry)
        self.assertIn("std::fma(x, scale.rx, scale.deltax)", geometry)
        self.assertIn("rayjoin_lsi_left_source", api)
        self.assertIn("rayjoin_right_segments", api)
        self.assertIn("rebuild_rayjoin_segment_scene", api)
        self.assertIn("run_rayjoin_lsi_aabb_refined_rows", api)
        self.assertIn("rayjoin_lsi_aabb_refined_collision_callback", api)
        self.assertIn("rtdl_embree_run_rayjoin_lsi_aabb_refined_segment_pair_intersections", api)
        self.assertIn("_call_rayjoin_lsi_aabb_refined_embree_packed", (ROOT / "src" / "rtdsl" / "embree_runtime.py").read_text(encoding="utf-8"))
        self.assertIn("predicate_mode", scene)
        self.assertIn("rayjoin_lsi_trace_segment", scene)
        self.assertIn("RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY", scene + api)
        self.assertIn("constexpr double kRayjoinLsiBoundsPad = kBvhCandidatePad", scene)
        self.assertIn("!segment_intersection(*state->probe, build, &point)", scene)

    def test_same_source_arcgis_targets_write_rayjoin_layout_but_not_preprocessed_claim(self) -> None:
        from rtdsl.rayjoin_paper_suite import same_source_arcgis_targets

        by_id = {target.target_id: target for target in same_source_arcgis_targets()}
        self.assertEqual(by_id["county"].output_relative_path, "point_cdb/dtl_cnty/dtl_cnty_Point.cdb")
        self.assertEqual(
            by_id["zipcode"].output_relative_path,
            "point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb",
        )
        self.assertIn("same_source_regenerated_cdb", by_id["county"].topology_contract)
        self.assertIn("not a recovered paper_preprocessed", by_id["county"].topology_contract)


if __name__ == "__main__":
    unittest.main()
