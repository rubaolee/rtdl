from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5808_owl_cgo_residual_claim.py"


def load_module():
    spec = importlib.util.spec_from_file_location("goal5808_owl_claim", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Goal5808 OWL claim verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5808OwlCgoResidualClaimTest(unittest.TestCase):
    def test_exact_frozen_evidence_reconstructs_honest_claim(self) -> None:
        result = load_module().build_claim()
        self.assertEqual(
            result["counts"],
            {
                "primary_semantic_residual": 3,
                "partial_enforcement_residual": 1,
                "executable_binding_support": 1,
                "all_invalid_controls_reached_launch": 5,
                "all_rtdl_controls_rejected_prelaunch": 5,
            },
        )
        self.assertEqual(
            result["effective_owl_source"]["repository"],
            "https://github.com/NVIDIA/OWL.git",
        )
        self.assertFalse(
            result["claim_boundary"]
            ["five_equally_independent_novel_mechanisms_claimed"]
        )
        self.assertFalse(
            result["claim_boundary"]["new_application_generalization_claimed"]
        )

    def test_cli_is_machine_readable_and_contains_no_performance_claim(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(
            result["status"],
            "PASS__BOUNDED_OWL_RESIDUAL_CGO_CLAIM_RECONSTRUCTED",
        )
        self.assertFalse(result["claim_boundary"]["performance_claimed"])
        self.assertEqual(len(result["mechanisms"]), 5)

    def test_authority_mutation_fails_closed(self) -> None:
        module = load_module()
        original = json.loads(module.TABLE.read_bytes())
        original["protocol_residual_ownership"][0]["rtdl"][
            "finding_count"] = 2
        with tempfile.TemporaryDirectory() as temporary:
            mutant = Path(temporary) / "mutant.json"
            mutant.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "digest mismatch"):
                module.build_claim(table_path=mutant)


if __name__ == "__main__":
    unittest.main()
