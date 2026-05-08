import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1495_v1_5_4_collect_k_device_pointer_abi_contract.py"


def load_contract_module():
    spec = importlib.util.spec_from_file_location("goal1495_contract", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1495V154CollectKDevicePointerAbiContractTest(unittest.TestCase):
    def test_contract_defines_separate_device_pointer_symbol(self) -> None:
        module = load_contract_module()

        contract = module.validate_contract(module.build_contract())

        self.assertEqual(contract["primitive"], "COLLECT_K_BOUNDED")
        self.assertNotEqual(contract["current_host_symbol"], contract["proposed_device_symbol"])
        self.assertIn("uint64_t candidate_rows_device_ptr", contract["proposed_c_abi"])
        self.assertIn("uint64_t rows_out_device_ptr", contract["proposed_c_abi"])

    def test_contract_requires_transfer_accounting_outputs(self) -> None:
        module = load_contract_module()
        contract = module.validate_contract(module.build_contract())

        self.assertIn("uint64_t* h2d_transfers_out", contract["proposed_c_abi"])
        self.assertIn("uint64_t* d2h_transfers_out", contract["proposed_c_abi"])
        self.assertIn("uint64_t* internal_device_transfers_out", contract["proposed_c_abi"])

    def test_rejects_claim_expansion(self) -> None:
        module = load_contract_module()
        contract = module.build_contract()
        contract["claim_flags"]["true_zero_copy_authorized"] = True

        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized=False"):
            module.validate_contract(contract)

    def test_rejects_reusing_host_symbol(self) -> None:
        module = load_contract_module()
        contract = module.build_contract()
        contract["proposed_device_symbol"] = contract["current_host_symbol"]

        with self.assertRaisesRegex(ValueError, "must not reuse"):
            module.validate_contract(contract)

    def test_markdown_contains_acceptance_tests_and_boundary(self) -> None:
        module = load_contract_module()
        markdown = module.to_markdown(module.validate_contract(module.build_contract()))

        self.assertIn("goal1492_fixture_same_rows_no_overflow", markdown)
        self.assertIn("does not implement the native symbol", markdown)
        self.assertIn("does not prove true zero-copy", markdown)


if __name__ == "__main__":
    unittest.main()
