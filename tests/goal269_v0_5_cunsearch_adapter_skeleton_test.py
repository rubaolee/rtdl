import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal269V05CuNSearchAdapterSkeletonTest(unittest.TestCase):
    def test_binary_resolution_uses_explicit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            binary = Path(tmpdir) / "cunsearch_stub"
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
            resolved = rt.resolve_cunsearch_binary(binary)
            self.assertEqual(resolved, binary.resolve())

    def test_missing_binary_is_reported_honestly(self) -> None:
        old = os.environ.pop("RTDL_CUNSEARCH_BIN", None)
        try:
            with self.assertRaisesRegex(
                RuntimeError,
                "cuNSearch adapter is not online yet; set RTDL_CUNSEARCH_BIN",
            ):
                rt.plan_cunsearch_fixed_radius_neighbors(radius=1.0, k_max=8)
        finally:
            if old is not None:
                os.environ["RTDL_CUNSEARCH_BIN"] = old

    def test_request_writer_emits_expected_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            binary = Path(tmpdir) / "cunsearch_stub"
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
            output = Path(tmpdir) / "request.json"
            written = rt.write_cunsearch_fixed_radius_request(
                output,
                query_points=(rt.Point3D(id=10, x=1.0, y=2.0, z=3.0),),
                search_points=(rt.Point3D(id=1, x=4.0, y=5.0, z=6.0),),
                radius=0.75,
                k_max=4,
                binary_path=binary,
            )
            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(payload["adapter"], "cunsearch")
            self.assertEqual(payload["workload"], "fixed_radius_neighbors")
            self.assertEqual(payload["target_dimension"], "3d")
            self.assertEqual(payload["radius"], 0.75)
            self.assertEqual(payload["k_max"], 4)
            self.assertEqual(payload["query_points"][0]["id"], 10)
            self.assertEqual(payload["search_points"][0]["z"], 6.0)

    def test_adapter_config_reports_planned_when_unconfigured(self) -> None:
        old = os.environ.pop("RTDL_CUNSEARCH_BIN", None)
        try:
            config = rt.cunsearch_adapter_config()
            self.assertEqual(config.current_status, "planned")
            self.assertIn("Linux host", config.notes)
        finally:
            if old is not None:
                os.environ["RTDL_CUNSEARCH_BIN"] = old


if __name__ == "__main__":
    unittest.main()
