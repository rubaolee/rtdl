from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal5792_artifact_identity_hygiene_audit.py"


def _module():
    spec = importlib.util.spec_from_file_location("goal5792_hygiene", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5792ArtifactIdentityHygieneAuditTest(unittest.TestCase):
    def test_real_frozen_artifacts_and_current_docs_pass(self):
        result = _module().build_result(ROOT)
        self.assertEqual(
            result["status"],
            "PASS__RC_PERFORMANCE_IDENTITY_SEPARATED__HISTORICAL_SCHEMA_RESIDUE_EXPLICIT",
        )
        self.assertEqual(result["schema"], "rtdl.goal5792.artifact_identity_hygiene_audit.v2")
        self.assertTrue(result["identity_separation"]["all_three_distinct"])
        self.assertEqual(
            result["historical_schema_residue"]["goal5776_schema_occurrence_count"],
            1175,
        )
        self.assertEqual(
            result["historical_schema_residue"]["goal5776_schema_json_member_count"],
            603,
        )
        self.assertFalse(result["historical_schema_residue"]["frozen_bytes_renamed_or_rewritten"])
        self.assertTrue(result["documentation_hygiene"]["responsibility_claim_narrowing_disclosed"])
        self.assertTrue(result["outer_performance_authority"][
            "evidence_embeds_exact_standalone_execution_source"])

    def test_expected_historical_schema_counter_is_exact(self):
        module = _module()
        self.assertEqual(sum(module.EXPECTED_GOAL5776_SCHEMAS.values()), 1175)
        self.assertEqual(module.EXPECTED_GOAL5776_SCHEMAS["rtdl.goal5776.real_scale_formal_worker.v1"], 464)
        self.assertEqual(module.EXPECTED_GOAL5776_SCHEMAS["rtdl.goal5776.registered_row_binding.v1"], 590)

    def test_outer_authority_or_embedded_source_drift_is_rejected(self):
        module = _module()
        authority = json.loads((ROOT / module.PINS["performance_result"][0]).read_text())
        bad = copy.deepcopy(authority)
        bad["run_goal_id"] = 5776
        with self.assertRaisesRegex(RuntimeError, "authority goal"):
            module._validate_performance_authority(
                bad, module.PINS["performance_source"][1])
        bad = copy.deepcopy(authority)
        bad["lineage"]["execution_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "source binding"):
            module._validate_performance_authority(
                bad, module.PINS["performance_source"][1])
        with self.assertRaisesRegex(RuntimeError, "embedded execution source"):
            module._validate_performance_authority(authority, "f" * 64)


if __name__ == "__main__":
    unittest.main()
