from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4607_v3_0_m208_python_ctypes_dlpack_like_metadata_bridge_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4607_v3_0_m208_python_ctypes_dlpack_like_metadata_bridge_2026-06-17.md"
EXAMPLE = ROOT / "examples/current/embedding/python_ctypes_dlpack_like_metadata_client.py"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
MATRIX_DOC = ROOT / "docs/learn/v3_0_binding_and_device_interop_matrix.md"


class Goal4607V30M208PythonCtypesDLPackLikeMetadataBridgeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4607_m208_v3_python_ctypes_dlpack_like_metadata_bridge")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_python_dlpack_like_metadata_bridge_checks_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.python_ctypes_dlpack_like_metadata_bridge.goal4607.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_smoke_runs_staged_python_bridge(self) -> None:
        smoke = self.checked_in["python_ctypes_dlpack_like_metadata_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(self.checked_in["checks"]["stage_bundle_smoke_ok"])
        self.assertTrue(self.checked_in["checks"]["staged_python_dlpack_like_metadata_example_runs"])
        stdout = smoke["run_result"]["stdout"]
        self.assertEqual(
            "python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument",
            stdout,
        )

    def test_report_index_example_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4607 / V3 M208", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4607 Python ctypes DLPack-like metadata bridge", INDEX.read_text(encoding="utf-8"))
        example = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("__dlpack__", example)
        self.assertIn("__dlpack_device__", example)
        self.assertIn("DLPack-like object to C ABI descriptor", MATRIX_DOC.read_text(encoding="utf-8"))
        self.assertEqual(
            "validated_metadata_only",
            self.checked_in["support_matrix"]["dlpack_like_to_c_abi_descriptor"],
        )
        self.assertEqual(
            "rejected_invalid_argument",
            self.checked_in["support_matrix"]["dlpack_like_descriptor_host_aabb2_query_route"],
        )

    def test_only_metadata_bridge_is_authorized(self) -> None:
        self.assertTrue(self.checked_in["claim_boundary"]["dlpack_like_metadata_bridge_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "dlpack_like_metadata_bridge_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
