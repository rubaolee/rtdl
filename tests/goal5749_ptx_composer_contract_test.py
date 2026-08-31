import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "history/internal_docs/goal5749_trusted_ptx_composer_compatibility_contract_20260811.json"
NATIVE = ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
RUNTIME = ROOT / "src/rtdsl/v4_optix_callback_runtime.py"
DIAGNOSTIC = ROOT / "scripts/goal5749_p1_two_module_diagnostic.py"
ATTACK_DRIVER = ROOT / "scripts/goal5749_p1_composer_attack_driver.py"


class TrustedPtxComposerContractTest(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.native = NATIVE.read_text(encoding="utf-8")
        self.runtime = RUNTIME.read_text(encoding="utf-8")

    def test_mechanism_substitution_is_explicit(self):
        disclosure = self.contract["architectural_disclosure"]
        self.assertTrue(disclosure["mechanism_substitution_is_explicit"])
        self.assertFalse(disclosure["accepted_goal5749_result_proves_cross_module_linking"])
        self.assertTrue(disclosure["accepted_goal5749_result_proves_single_module_composition"])

    def test_trust_boundary_never_accepts_original_callable_or_user_ptx(self):
        trust = self.contract["trust_boundary"]
        self.assertFalse(trust["original_user_python_callable_compiled"])
        self.assertFalse(trust["raw_user_ptx_or_cuda_accepted"])
        self.assertTrue(trust["verified_callback_ir_digest_required"])
        self.assertTrue(trust["generated_python_source_digest_required"])

    def test_exact_toolchain_and_upgrade_gate_are_frozen(self):
        matrix = self.contract["exact_toolchain_matrix"]
        self.assertEqual(matrix["numba"], "0.65.1")
        self.assertEqual(matrix["optix_sdk"], "9.0.0")
        self.assertEqual(matrix["ptx_isa"], "8.7")
        self.assertEqual([row["compute_capability"] for row in matrix["targets"]],
                         [[6, 1], [8, 9]])
        self.assertTrue(matrix["any_version_or_target_change_requires_fail_closed_revalidation_and_review"])

    def test_native_enforces_identity_and_environment_fail_closed_rules(self):
        for token in (
            "V4 wrapper/leaf PTX target identity mismatch",
            "V4 leaf symbol identities are not unique",
            "V4 leaf PTX lacks its bound ABI symbol",
            "V4 leaf PTX contains another leaf's ABI symbol",
            "V4 wrapper PTX has an unrecognized or ambiguous extern declaration",
            "V4 wrapper PTX leaf extern identity mismatch",
            "V4 Numba environment symbol is referenced by leaf PTX",
            "V4 leaf PTX has multiple Numba environment declarations",
            "V4 verified leaf PTX acquired an external dependency",
        ):
            self.assertIn(token, self.native)

    def test_debug_loss_and_scale_are_disclosed(self):
        limits = self.contract["known_limits"]
        self.assertFalse(limits["leaf_debug_line_information_available_after_composition"])
        self.assertEqual(
            limits["goal5749_scale"],
            "three_spheres__three_rays__trace_depth_one__one_geometry_contract")
        self.assertFalse(limits["general_ptx_linker_claimed"])

    def test_future_receipt_requires_interpreter_digest(self):
        obligations = self.contract["runtime_obligations"]
        self.assertTrue(obligations[
            "callback_ir_interpreter_output_digest_must_be_serialized_in_future_receipts"])
        self.assertIn("interpreter_output_sha256", self.runtime)

    def test_two_module_diagnostic_is_separate_and_zero_timing(self):
        text = DIAGNOSTIC.read_text(encoding="utf-8")
        self.assertIn("ordinary_external_two_module_diagnostic", text)
        self.assertIn('"registered_performance_timing_count": 0', text)
        self.assertIn('"accepted_goal5749_result_rerun_or_changed": False', text)
        self.assertIn("rtdl_optix_v4_run_verified_callback_two_module_diagnostic", self.runtime)
        self.assertIn("__direct_callable__rtdl_v4_leaf_module_anchor", self.native)

    def test_behavioral_attack_driver_covers_composer_boundaries(self):
        text = ATTACK_DRIVER.read_text(encoding="utf-8")
        for name in (
            "target_identity_mismatch",
            "numba_environment_second_occurrence",
            "multiple_numba_environment_declarations",
            "new_external_dependency",
            "duplicate_leaf_symbol_identity",
        ):
            self.assertIn(name, text)
        self.assertIn('"registered_performance_timing_count": 0', text)

    def test_goal5750_and_performance_remain_blocked(self):
        acceptance = self.contract["acceptance"]
        self.assertFalse(acceptance["goal5750_allowed_before_owner_returned_review_closes_p1"])
        self.assertFalse(acceptance["performance_or_app_migration_authorized"])


if __name__ == "__main__":
    unittest.main()
