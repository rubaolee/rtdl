import unittest
from pathlib import Path

from rtdsl.python_rtdl_app_purity import native_symbol_purity_audit


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
REPORT = ROOT / "docs" / "reports" / "goal1680_current_native_app_leakage_gap_2026-05-10.md"


class Goal1708SourceRecoveryAndSemanticCleanupTest(unittest.TestCase):
    def _native_text(self) -> str:
        chunks = []
        for path in NATIVE.rglob("*"):
            if path.is_file():
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        return "\n".join(chunks)

    def test_embree_recovered_files_are_not_truncated(self):
        api_text = (NATIVE / "embree" / "rtdl_embree_api.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        prelude_text = (NATIVE / "embree" / "rtdl_embree_prelude.h").read_text(
            encoding="utf-8", errors="ignore"
        )

        self.assertIn("RTDL_EMBREE_EXPORT void rtdl_embree_free_rows", api_text)
        self.assertIn("}  // extern \"C\"", prelude_text)
        self.assertFalse(api_text.rstrip().endswith("std::sort(rows.begin(), row"))
        self.assertGreater(api_text.count("RTDL_EMBREE_EXPORT"), 20)

    def test_stale_replay_artifacts_are_absent(self):
        native_text = self._native_text()
        for stale in (
            "db_copy_dataset_table",
            "DB columnar inputs must not be null",
            "field_index_count",
            "rtdl_embree_run_lsi",
            "rtdl_optix_run_lsi",
            "rtdl_embree_run_overlay",
            "rtdl_optix_run_overlay",
            "rtdl_embree_run_triangle_probe",
            "rtdl_optix_run_triangle_probe",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, native_text)

    def test_columnar_payload_validation_uses_fields_not_stale_columns(self):
        for path in (
            NATIVE / "optix" / "rtdl_optix_workloads.cpp",
            NATIVE / "vulkan" / "rtdl_vulkan_core.cpp",
        ):
            text = path.read_text(encoding="utf-8", errors="ignore")
            with self.subTest(path=path):
                self.assertIn("payload fields must not be null", text)
                self.assertNotIn("if (!columns || field_count == 0)", text)
                self.assertNotIn("columns[index]", text)

    def test_legacy_purity_symbols_remain_zero(self):
        audit = native_symbol_purity_audit(repo_root=ROOT)
        self.assertEqual(tuple(audit["legacy_engine_customized_symbols"]), ())
        self.assertFalse(audit["pure_native_app_contract_ready"])

    def test_current_gate_report_keeps_blocked_phrase(self):
        report_text = REPORT.read_text(encoding="utf-8")
        self.assertIn("The native app-agnostic release gate still fails.", report_text)
        self.assertIn("RTDL native internals are fully app-agnostic.", report_text)


if __name__ == "__main__":
    unittest.main()
