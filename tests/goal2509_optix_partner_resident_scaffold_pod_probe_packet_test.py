import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2509_optix_partner_resident_scaffold_pod_probe_packet_2026-05-22.md"
SCRIPT = ROOT / "scripts/goal2509_optix_partner_resident_scaffold_probe_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2509_optix_partner_resident_scaffold_probe_pod_2026-05-22.json"


class Goal2509OptixPartnerResidentScaffoldPodProbePacketTest(unittest.TestCase):
    def test_pod_probe_script_records_real_cuda_descriptor_and_fail_closed_symbol(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("torch.arange", text)
        self.assertIn("prepare_partner_resident_columnar_record_set", text)
        self.assertIn("prepare_optix_partner_resident_columnar_record_set", text)
        self.assertIn("allow_scaffold_probe=True", text)
        self.assertIn("expected_fail_closed", text)
        self.assertIn("fail-closed ABI scaffold", text)
        self.assertIn("goal2509_optix_partner_resident_scaffold_probe_pod_2026-05-22.json", text)

    def test_report_records_probe_requirements(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2509", text)
        self.assertIn("GPU pod required", text)
        self.assertIn("build/librtdl_optix.so", text)
        self.assertIn("expected_fail_closed", text)
        self.assertIn("not a performance run", text)
        self.assertIn("native execution remains unauthorized", text)

    def test_pod_artifact_records_expected_fail_closed_probe(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["cuda_available"])
        self.assertEqual(payload["probe_status"], "expected_fail_closed")
        self.assertEqual(
            payload["native_symbol"],
            "rtdl_optix_columnar_payload_create_from_device_columns",
        )
        self.assertIn("fail-closed ABI scaffold", payload["error"])
        self.assertEqual(payload["descriptor"]["device"], "cuda:0")
        self.assertEqual(payload["descriptor"]["field_names"], ["row_id", "region_id", "ship_year", "revenue"])
        self.assertIn("torch", payload["descriptor"]["source_protocols"])


if __name__ == "__main__":
    unittest.main()
