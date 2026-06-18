from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4609_v3_0_m210_archive_stage_c_examples_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4609_v3_0_m210_archive_stage_c_examples_smoke_2026-06-17.md"
STAGING_CONTRACT = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md"
EMBEDDING_README = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/README.md"
ARCHITECTURE_DOC = ROOT / "docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md"
BINDING_MATRIX = ROOT / "docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4609V30M210ArchiveStageCExamplesSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4609_m210_v3_archive_stage_c_examples_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_archive_stage_c_examples_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.archive_stage_c_examples.goal4609.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_archive_stage_c_examples_compile_and_run(self) -> None:
        smoke = self.checked_in["archive_stage_c_examples_smoke"]
        self.assertTrue(smoke["ok"])
        by_script = {row["script"]: row for row in smoke["example_runs"]}
        self.assertEqual(
            "direct_link_ok 0.1.3 ok",
            by_script["c_api_direct_link_client.c"]["run_result"]["stdout"],
        )
        self.assertEqual(
            "hit_count=1 first_pair=(0,0)",
            by_script["c_api_aabb2_overlap_client.c"]["run_result"]["stdout"],
        )
        self.assertIn(
            "validated_host_external_runtime_cases=3",
            by_script["c_api_host_runtime_client.c"]["run_result"]["stdout"],
        )
        self.assertIn(
            "validated_cuda_buffer_metadata_cases=4",
            by_script["c_api_cuda_buffer_metadata_client.c"]["run_result"]["stdout"],
        )
        self.assertIn(
            "validated_last_error_diagnostics_cases=7",
            by_script["c_api_last_error_client.c"]["run_result"]["stdout"],
        )
        for row in by_script.values():
            self.assertTrue(row["compile_result"]["ok"], row["script"])
            self.assertTrue(row["run_result"]["ok"], row["script"])
            self.assertTrue(row["ok"], row["script"])

    def test_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4609 / V3 M210", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4609 archive-stage C examples smoke", INDEX.read_text(encoding="utf-8"))
        self.assertIn("extracted source-tree archive carries runnable C examples", STAGING_CONTRACT.read_text(encoding="utf-8"))
        self.assertIn("extracted archive also carries runnable C examples", EMBEDDING_README.read_text(encoding="utf-8"))
        self.assertIn("As of Goal4610", ARCHITECTURE_DOC.read_text(encoding="utf-8"))
        self.assertIn("C examples from archive stage", BINDING_MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["archive_c_examples_stage_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "archive_c_examples_stage_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
