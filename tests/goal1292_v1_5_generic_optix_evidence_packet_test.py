from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1292_v1_5_generic_optix_evidence_packet as packet
from scripts import goal1292_v1_5_generic_optix_evidence_runner as runner


ROOT = Path(__file__).resolve().parents[1]


class Goal1292V15GenericOptixEvidencePacketTest(unittest.TestCase):
    def test_packet_targets_generic_primitives_and_graph_wrapper(self) -> None:
        payload = packet.build_packet()

        self.assertEqual(payload["active_backends"], ["embree", "optix"])
        self.assertEqual(payload["frozen_backends_before_v2_1"], ["vulkan", "hiprt", "apple_rt"])
        self.assertIn("rtdl_pod_env_probe.sh", payload["env_probe"]["script"])
        self.assertIn("nvidia_smi_tail", payload["env_probe"]["required_fields"])
        self.assertIn("make build-optix", "\n".join(payload["commands"]["prepare"]))
        self.assertIn("goal1292_v1_5_generic_optix_evidence_runner.py", payload["commands"]["primitive_runner"])
        runner_text = (ROOT / "scripts" / "goal1292_v1_5_generic_optix_evidence_runner.py").read_text()
        self.assertIn("run_generic", runner_text)
        self.assertIn("--visibility-query-repeats 100", payload["commands"]["graph_wrapper"])
        self.assertFalse(payload["public_wording_authorized"])
        self.assertIn("Embree prepared-scene parity", payload["known_gap"])
        self.assertIn("whole-app speedup claims", payload["boundary"])

    def test_runner_cpu_sanity_records_oracle_and_boundaries(self) -> None:
        payload = runner.build_payload(
            copies=3,
            backends=("cpu",),
            query_repeats=2,
            skip_prepared=True,
        )

        self.assertEqual(payload["fixture"]["ray_count"], 6)
        self.assertEqual(payload["fixture"]["triangle_count"], 3)
        self.assertEqual(payload["fixture"]["expected_hit_count"], 3)
        self.assertEqual(payload["direct_anyhit_count"]["cpu"]["status"], "ok")
        self.assertEqual(payload["direct_anyhit_count"]["cpu"]["hit_count"], 3)
        self.assertIsNone(payload["prepared_optix_anyhit_count"])
        self.assertFalse(payload["public_wording_authorized"])
        self.assertEqual(payload["frozen_backends_before_v2_1"], ["vulkan", "hiprt", "apple_rt"])

    def test_packet_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_json = tmp_path / "packet.json"
            output_md = tmp_path / "packet.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1292_v1_5_generic_optix_evidence_packet.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("primitive_runner", payload["commands"])
            self.assertIn("Generic OptiX Evidence Packet", markdown)
            self.assertIn("Required Artifacts", markdown)

    def test_runner_cli_writes_cpu_output_without_pod(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "runner.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1292_v1_5_generic_optix_evidence_runner.py",
                    "--copies",
                    "2",
                    "--backend",
                    "cpu",
                    "--skip-prepared",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["direct_anyhit_count"]["cpu"]["status"], "ok")
            self.assertEqual(payload["direct_anyhit_count"]["cpu"]["hit_count"], 2)


if __name__ == "__main__":
    unittest.main()
