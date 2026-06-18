from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
STAGING_CONTRACT = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md"
EMBEDDING_README = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/README.md"


class Goal4597V30M198PrefixStagePythonCtypesSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4597_m198_v3_prefix_stage_python_ctypes_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_prefix_stage_python_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.prefix_stage_python_ctypes.goal4597.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_prefix_stage_python_examples_run(self) -> None:
        smoke = self.checked_in["prefix_stage_python_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertEqual("/opt/rtdl", smoke["prefix"])
        by_script = {row["script"]: row for row in smoke["example_runs"]}
        self.assertEqual("python_ctypes_ok 0.1.3 ok", by_script["python_ctypes_client.py"]["stdout"])
        self.assertEqual(
            "python_ctypes_hit_count=1 first_pair=(0,0)",
            by_script["python_ctypes_aabb2_query_client.py"]["stdout"],
        )
        self.assertEqual(
            "python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument",
            by_script["python_ctypes_cuda_buffer_metadata_client.py"]["stdout"],
        )
        self.assertEqual(
            "python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument",
            by_script["python_ctypes_dlpack_like_metadata_client.py"]["stdout"],
        )
        for row in by_script.values():
            self.assertTrue(row["ok"], row["script"])

    def test_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4597 / V3 M198", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4597 prefix-stage Python ctypes smoke", INDEX.read_text(encoding="utf-8"))
        self.assertIn("python_ctypes_client.py", STAGING_CONTRACT.read_text(encoding="utf-8"))
        self.assertIn("without using\nsource-tree relative paths", EMBEDDING_README.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["prefix_python_ctypes_stage_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "prefix_python_ctypes_stage_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
