from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "goal5753-held-out-particle-tracking"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Goal5753HeldOutParticleTrackingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.attempt = load("goal5753_attempt_test", APP / "callback_attempt.py")
        self.contract = load("goal5753_contract_test", APP / "physical_contract.py")
        self.oracle = load("goal5753_oracle_test", APP / "independent_oracle.py")

    def test_restricted_callback_frontend_passes_but_frozen_wrapper_fails_closed(self) -> None:
        from rtdsl.v4_callback_abi import compile_callback_abi
        from rtdsl.v4_callback_frontend import compile_callback_source
        from rtdsl.v4_callback_optix_wrapper_codegen import (
            CallbackWrapperCodegenError,
            generate_trusted_optix_wrapper_v1,
        )

        verified = compile_callback_source(self.attempt.CALLBACK_SOURCE, self.attempt.manifest())
        self.assertIsNone(verified.program.manifest.any_hit_delivery)
        abi = compile_callback_abi(verified)
        with self.assertRaises(CallbackWrapperCodegenError) as caught:
            generate_trusted_optix_wrapper_v1(
                verified, abi, any_hit_proof_authority=None
            )
        self.assertEqual(caught.exception.code, "physical_template")

    def test_physical_capability_rejection_names_every_missing_family(self) -> None:
        with self.assertRaises(self.contract.PhysicalAdmissionError) as caught:
            self.contract.admit_required_physical_capabilities(
                self.attempt.REQUIRED_PHYSICAL_CAPABILITIES
            )
        self.assertEqual(caught.exception.code, self.contract.FAILURE_CODE)
        self.assertEqual(
            set(caught.exception.missing),
            {"geometry_family", "primitive_columns", "hit_channels", "query_columns", "output_columns"},
        )

    def test_exact_oracle_locates_both_tetrahedra(self) -> None:
        vertices, cells = self.oracle.two_tetra_fixture()
        self.assertEqual(
            self.oracle.locate_cell(
                self.oracle.point(Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)),
                vertices, cells,
            ),
            0,
        )
        self.assertEqual(
            self.oracle.locate_cell(
                self.oracle.point(Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)),
                vertices, cells,
            ),
            1,
        )

    def test_oracle_fails_closed_on_boundary_and_outside(self) -> None:
        vertices, cells = self.oracle.two_tetra_fixture()
        for query, matches in (
            (self.oracle.point(Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)), (0, 1)),
            (self.oracle.point(2, 2, 2), ()),
        ):
            self.assertEqual(self.oracle.containing_cells(query, vertices, cells), matches)
            with self.assertRaises(ValueError):
                self.oracle.locate_cell(query, vertices, cells)

    def test_selection_is_irrevocable_and_selected_before_app_files(self) -> None:
        selection = json.loads((
            ROOT / "history/internal_docs/goal5753_held_out_selection_20260811.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(
            selection["selection"]["selected_candidate"]["candidate_id"],
            "Wang2022AnGP::particle_tracking",
        )
        self.assertFalse(selection["selection"]["replacement_allowed"])
        commit_files = subprocess.run(
            ["git", "show", "--name-only", "--format=", "b8058860f"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        self.assertFalse(any("goal5753-held-out-particle-tracking" in value for value in commit_files))

    def test_frozen_core_and_native_have_zero_diff(self) -> None:
        seal = json.loads((
            ROOT / "history/internal_docs/goal5753_frozen_core_seal_audit_postselection_20260811.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(seal["status"], "exact_goal5752_core_and_native_unchanged")
        self.assertEqual(seal["held_out_exam_core_diff_count"], 0)
        self.assertEqual(seal["missing"], [])
        self.assertEqual(seal["added"], [])
        self.assertEqual(seal["changed"], [])


if __name__ == "__main__":
    unittest.main()
