from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2348_v2_2_rtnn_external_runner_2026-05-18.md"


def _load_runner():
    spec = importlib.util.spec_from_file_location("goal2348_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load goal2348 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal2348RtnnV22ExternalRunnerTest(unittest.TestCase):
    def test_parse_rtnn_timing_lines(self) -> None:
        runner = _load_runner()
        timings = runner.parse_rtnn_timings(
            "time search compute: 1.25 ms\n"
            "noise\n"
            "time result copy D2H: 0.50 ms\n"
            "time search compute: 1.75 ms\n"
        )
        self.assertEqual(timings["search compute"], [1.25, 1.75])
        self.assertEqual(timings["result copy D2H"], [0.5])

    def test_generate_point_file_is_deterministic_rtnn_xyz(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            first = pathlib.Path(tmp) / "a.txt"
            second = pathlib.Path(tmp) / "b.txt"
            runner.generate_uniform_point_file(first, point_count=4, dimension=2, seed=7)
            runner.generate_uniform_point_file(second, point_count=4, dimension=2, seed=7)
            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            rows = first.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(len(row.split(",")) == 3 for row in rows))
            self.assertTrue(all(row.endswith(",0.000000000") for row in rows))

    def test_cli_generate_writes_boundary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            point_file = pathlib.Path(tmp) / "points.txt"
            json_out = pathlib.Path(tmp) / "out.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "generate",
                    "--point-file",
                    str(point_file),
                    "--point-count",
                    "3",
                    "--dimension",
                    "3",
                    "--json-out",
                    str(json_out),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(payload["generated"]["format"], "rtnn_csv_xyz")
            self.assertFalse(payload["claim_boundary"]["paper_dataset"])
            self.assertTrue(payload["claim_boundary"]["synthetic_input_only"])

    def test_rtdl_smoke_loader_uses_public_record_shape(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('{"id": idx, "x": x, "y": y}', text)
        self.assertNotIn("rt.Point2D", text)

    def test_cuda12_patch_command_is_idempotent_and_external_only(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / "src" / "optixNSearch"
            source.mkdir(parents=True)
            (source / "thrust_helper.cu").write_text(
                "#include <thrust/execution_policy.h>\nvoid f() {}\n",
                encoding="utf-8",
            )
            (source / "func.h").write_text(
                "#pragma once\n#include <thrust/device_vector.h>\n",
                encoding="utf-8",
            )
            (source / "search.cpp").write_text(
                "#include <thrust/device_vector.h>\nvoid s() {}\n",
                encoding="utf-8",
            )
            (source / "sort.cpp").write_text(
                "#include <thrust/gather.h>\nvoid g() { thrust::host_vector<int> v; }\n",
                encoding="utf-8",
            )
            (source / "util.cpp").write_text(
                "#include <thrust/device_vector.h>\nvoid u() {}\n",
                encoding="utf-8",
            )
            (source / "geometry.cu").write_text(
                "float a = uint_as_float(1); unsigned b = float_as_uint(1.0f);\n",
                encoding="utf-8",
            )

            first = runner.patch_rtnn_cuda12_checkout(root)
            self.assertEqual(first["operation"], "patch-rtnn-cuda12")
            self.assertEqual(first["changed_count"], 7)
            self.assertFalse(first["claim_boundary"]["rtdl_source_changed"])
            self.assertFalse(first["claim_boundary"]["algorithm_changed"])
            self.assertIn("thrust/count.h", (source / "thrust_helper.cu").read_text(encoding="utf-8"))
            self.assertIn("thrust/host_vector.h", (source / "sort.cpp").read_text(encoding="utf-8"))
            self.assertIn("__CUDA_ARCH_LIST__ 600", (source / "func.h").read_text(encoding="utf-8"))
            self.assertIn("__CUDA_ARCH_LIST__ 600", (source / "search.cpp").read_text(encoding="utf-8"))
            self.assertIn("__CUDA_ARCH_LIST__ 600", (source / "sort.cpp").read_text(encoding="utf-8"))
            self.assertIn("__CUDA_ARCH_LIST__ 600", (source / "util.cpp").read_text(encoding="utf-8"))
            geometry = (source / "geometry.cu").read_text(encoding="utf-8")
            self.assertIn("__uint_as_float", geometry)
            self.assertIn("__float_as_uint", geometry)

            second = runner.patch_rtnn_cuda12_checkout(root)
            self.assertEqual(second["changed_count"], 0)

    def test_cli_cuda12_patch_writes_boundary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "rtnn"
            source = root / "src" / "optixNSearch"
            source.mkdir(parents=True)
            (source / "thrust_helper.cu").write_text(
                "#include <thrust/execution_policy.h>\n",
                encoding="utf-8",
            )
            (source / "func.h").write_text("#include <thrust/device_vector.h>\n", encoding="utf-8")
            (source / "search.cpp").write_text("#include <thrust/device_vector.h>\n", encoding="utf-8")
            (source / "sort.cpp").write_text("#include <thrust/gather.h>\n", encoding="utf-8")
            (source / "util.cpp").write_text("#include <thrust/device_vector.h>\n", encoding="utf-8")
            (source / "geometry.cu").write_text(
                "uint_as_float(1); float_as_uint(1.0f);\n",
                encoding="utf-8",
            )
            json_out = pathlib.Path(tmp) / "patch.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "patch-rtnn-cuda12",
                    "--rtnn-root",
                    str(root),
                    "--json-out",
                    str(json_out),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertTrue(payload["claim_boundary"]["external_rtnn_source_patch_only"])
            self.assertEqual(payload["changed_count"], 7)

    def test_report_names_runner_as_next_harness(self) -> None:
        campaign = (
            ROOT
            / "docs"
            / "reports"
            / "goal2346_v2_2_rtnn_nearest_neighbor_campaign_2026-05-18.md"
        ).read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("pod-ready RTNN harness", campaign)
        self.assertIn("parse RTNN timing blocks into JSON", campaign)
        self.assertIn("scripts/goal2348_rtnn_v2_2_external_runner.py", report)
        self.assertIn("current-v2.1 2-D smoke evidence", report)
        self.assertIn("v2.2 3-D bounded-neighbor evidence", report)
        self.assertIn("accept-with-boundary", report)


if __name__ == "__main__":
    unittest.main()
