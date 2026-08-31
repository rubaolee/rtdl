from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal5792_source_backed_responsibility_audit.py"


def _module():
    spec = importlib.util.spec_from_file_location("goal5792_responsibility_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5792SourceBackedResponsibilityAuditTest(unittest.TestCase):
    def test_real_frozen_source_rebuilds_nine_app_structural_result(self):
        result = _module().build_result(ROOT)
        self.assertEqual(
            result["status"],
            "PASS__NINE_APP_SOURCE_BACKED_STRUCTURAL_AUDIT__LEGACY_LEDGER_CLAIMS_NARROWED",
        )
        self.assertEqual(result["schema"], "rtdl.goal5792.source_backed_responsibility_audit.v3")
        self.assertEqual(result["summary"]["application_count"], 9)
        self.assertEqual(result["summary"]["v2_direct_executed_site_count"], 9)
        self.assertEqual(result["summary"]["v4_application_manual_low_level_api_hit_count"], 0)
        self.assertEqual(result["summary"]["application_developer_task_measurement_count"], 0)
        self.assertTrue(result["summary"]["structural_responsibility_shift_supported"])
        self.assertFalse(result["summary"]["application_productivity_improvement_supported"])
        self.assertEqual(result["summary"]["legacy_removed_obligation_fully_source_backed_count"], 0)
        self.assertEqual(result["summary"]["legacy_removed_obligation_partially_source_backed_count"], 2)
        self.assertEqual(result["summary"]["legacy_removed_obligation_not_established_count"], 4)
        self.assertEqual(
            result["summary"]["native_runtime_loading_behind_registered_v4_interface_count"], 8)
        self.assertEqual(result["summary"]["native_runtime_loading_exception_applications"], ["raydb"])
        self.assertEqual(len(result["legacy_removed_obligation_dispositions"]), 6)
        self.assertEqual({row["app"] for row in result["rows"]}, set(_module().APP_SPECS))
        self.assertTrue(all(row["v2_executed_direct_site"]["required_calls_present"] for row in result["rows"]))
        self.assertTrue(all(not row["v4_application_site"]["manual_low_level_optix_cuda_ptx_api_hits"] for row in result["rows"]))
        rows = {row["app"]: row for row in result["rows"]}
        self.assertFalse(rows["raydb"]["native_runtime_loading_behind_registered_v4_interface"])
        self.assertTrue(all(
            row["native_runtime_loading_behind_registered_v4_interface"]
            for app, row in rows.items() if app != "raydb"
        ))

    def test_forbidden_v4_manual_api_vocabulary_is_fail_closed(self):
        module = _module()
        clean = b"def app():\n    return 'registered interface'\n"
        hostile = clean + b"optixPipelineCreate(context, options)\n"
        self.assertFalse(any(token in clean for token in module.FORBIDDEN_V4_APP_BYTES))
        self.assertTrue(any(token in hostile for token in module.FORBIDDEN_V4_APP_BYTES))

    def test_mutated_ledger_is_rejected_before_claim_rebuild(self):
        module = _module()
        original = ROOT / module.LEDGER_REL
        with tempfile.TemporaryDirectory() as directory:
            fake_root = Path(directory)
            target = fake_root / module.LEDGER_REL
            target.parent.mkdir(parents=True)
            target.write_bytes(original.read_bytes() + b"\n")
            archive = fake_root / module.ARCHIVE_REL
            archive.parent.mkdir(parents=True)
            archive.write_bytes((ROOT / module.ARCHIVE_REL).read_bytes())
            predecessor = fake_root / module.V1_RESULT_REL
            predecessor.parent.mkdir(parents=True, exist_ok=True)
            predecessor.write_bytes((ROOT / module.V1_RESULT_REL).read_bytes())
            v2_predecessor = fake_root / module.V2_RESULT_REL
            v2_predecessor.parent.mkdir(parents=True, exist_ok=True)
            v2_predecessor.write_bytes((ROOT / module.V2_RESULT_REL).read_bytes())
            with self.assertRaisesRegex(RuntimeError, "responsibility-ledger SHA mismatch"):
                module.build_result(fake_root)


if __name__ == "__main__":
    unittest.main()
