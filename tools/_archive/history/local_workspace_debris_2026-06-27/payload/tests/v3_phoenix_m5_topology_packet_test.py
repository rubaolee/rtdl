import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m5_topology_rerun_packet_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m5_topology_rerun_packet_2026-06-20.md"


class V3PhoenixM5TopologyPacketTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_is_not_release_authorization(self):
        payload = self.payload()
        self.assertEqual(payload["goal4392_gate"], "M5")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        self.assertIn("point_location_topology_stream", payload["primary_generic_capabilities"])
        self.assertIn("compact_positive_stream", payload["primary_generic_capabilities"])

    def test_author_code_blocker_is_explicit(self):
        payload = self.payload()
        scope = payload["scope"]
        self.assertTrue(scope["full_m5_author_code_completion_requires_query_exec"])
        self.assertTrue(scope["query_exec_known_missing_on_current_pod_preflight"])
        self.assertIn("Record M5 author-code blocker", scope["if_query_exec_missing"])
        commands = {row["id"]: row for row in payload["required_commands"]}
        self.assertIn("author_query_exec_preflight", commands)
        preflight_command = commands["author_query_exec_preflight"]["command"]
        self.assertIn("rayjoin_query_exec_status.txt", preflight_command)
        self.assertIn("timeout 20s", preflight_command)
        self.assertIn("-maxdepth", preflight_command)

    def test_required_commands_cover_pip_and_overlay_same_contract(self):
        payload = self.payload()
        commands = {row["id"]: row for row in payload["required_commands"]}
        for required in [
            "env_probe",
            "optix_hardware_gate",
            "native_build",
            "m5_local_graph_gate",
            "author_query_exec_preflight",
            "m5_pip_point_location_rtdl_parity_filtered_100k",
            "m5_overlay_active_count_same_contract",
            "m5_topology_intake",
        ]:
            self.assertIn(required, commands)
            self.assertTrue(commands[required]["required"])
        self.assertIn("source_manifest.sha256", commands["env_probe"]["command"])
        self.assertIn("--require-rt-hardware", commands["optix_hardware_gate"]["command"])
        pip_command = commands["m5_pip_point_location_rtdl_parity_filtered_100k"]["command"]
        self.assertIn("--point-count 100000", pip_command)
        self.assertIn("--filter-backend-parity", pip_command)
        self.assertIn("--correctness-sample 100000", pip_command)
        self.assertIn("--optix-repeats 1000", pip_command)
        self.assertIn("--embree-repeats 1000", pip_command)
        self.assertIn("goal4373_rayjoin_cdb_point_location_compare.py", pip_command)
        overlay_command = commands["m5_overlay_active_count_same_contract"]["command"]
        self.assertIn("v3_0_m33_rayjoin_overlay_active_count_same_contract.py", overlay_command)
        self.assertIn("br_county_start256_count512.cdb", overlay_command)
        self.assertIn("br_soil_start256_count512.cdb", overlay_command)
        intake_command = commands["m5_topology_intake"]["command"]
        self.assertIn("v3_phoenix_m5_topology_intake.py", intake_command)
        self.assertIn("m5_topology_intake_summary.json", intake_command)

    def test_report_keeps_boundaries_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not release evidence",
            "does not authorize public speedup wording",
            "Phoenix M7-qualified release rows: 0",
            "source_manifest.sha256",
            "query_exec",
            "author-code completion as blocked",
            "OptiX/RT hardware gate",
            "backend-parity filter",
            "repeat counts are equal at 1000",
            "m5_topology_intake_summary.json",
            "overlay_active_pair_dependency_count",
            "full polygon overlay",
            "RayJoin paper reproduction",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
