import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1494_v1_5_4_collect_k_optix_abi_classification.py"


def load_classification_module():
    spec = importlib.util.spec_from_file_location("goal1494_classification", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1494V154CollectKOptixAbiClassificationTest(unittest.TestCase):
    def test_current_collect_k_symbol_is_classified_as_host_pointer_api(self) -> None:
        module = load_classification_module()

        report = module.validate_classification(module.classify_collect_k_optix_abi())

        self.assertTrue(report["signature_present"])
        self.assertTrue(report["host_pointer_api"])
        self.assertFalse(report["device_buffer_api"])
        self.assertFalse(report["accepted_for_goal1493_device_buffer_execution"])

    def test_rejects_device_buffer_claim_for_current_symbol(self) -> None:
        module = load_classification_module()
        report = module.classify_collect_k_optix_abi()
        report["device_buffer_api"] = True

        with self.assertRaisesRegex(ValueError, "device-buffer API"):
            module.validate_classification(report)

    def test_markdown_preserves_claim_boundary(self) -> None:
        module = load_classification_module()
        markdown = module.to_markdown(module.validate_classification(module.classify_collect_k_optix_abi()))

        self.assertIn("host_pointer_api=True", markdown)
        self.assertIn("Device-buffer API class", markdown)
        self.assertIn("does not prove true zero-copy", markdown)


if __name__ == "__main__":
    unittest.main()
