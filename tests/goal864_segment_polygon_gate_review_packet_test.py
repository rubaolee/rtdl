from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal864_segment_polygon_gate_review_packet as goal864


ROOT = Path(__file__).resolve().parents[1]


def _payload(*, host_ok: bool = False, native_ok: bool = False, include_postgis: bool = False, postgis_ok: bool = False) -> dict[str, object]:
    records = [
        {
            "label": "cpu_python_reference",
            "status": "ok",
            "sec": 0.01,
            "row_digest": {"row_count": 2, "sha256": "cpu"},
            "parity_vs_cpu_python_reference": True,
        },
        {
            "label": "optix_host_indexed",
            "status": "ok" if host_ok else "unavailable_or_failed",
            "sec": 0.02,
            "optix_mode": "host_indexed",
            "row_digest": {"row_count": 2, "sha256": "cpu" if host_ok else "other"},
            "parity_vs_cpu_python_reference": host_ok,
        },
        {
            "label": "optix_native",
            "status": "ok" if native_ok else "unavailable_or_failed",
            "sec": 0.03,
            "optix_mode": "native",
            "row_digest": {"row_count": 2, "sha256": "cpu" if native_ok else "other"},
            "parity_vs_cpu_python_reference": native_ok,
        },
    ]
    if include_postgis:
        records.append(
            {
                "label": "postgis",
                "status": "ok" if postgis_ok else "unavailable_or_failed",
                "sec": 0.04,
                "postgis_query_sec": 0.04,
                "row_digest": {"row_count": 2, "sha256": "cpu" if postgis_ok else "other"},
                "parity_vs_cpu_python_reference": postgis_ok,
            }
        )
    return {
        "goal": "Goal807 segment/polygon OptiX native-mode gate",
        "dataset": "authored_segment_polygon_minimal",
        "include_postgis": include_postgis,
        "status": "pass" if host_ok and native_ok and (not include_postgis or postgis_ok) else "non_strict_recorded_gaps",
        "strict_pass": host_ok and native_ok and (not include_postgis or postgis_ok),
        "strict_failures": [] if host_ok and native_ok and (not include_postgis or postgis_ok) else ["gap"],
        "records": records,
    }


class Goal864SegmentPolygonGateReviewPacketTest(unittest.TestCase):
    def test_local_missing_optix_becomes_needs_real_optix_artifact(self) -> None:
        packet = goal864.build_packet(_payload())
        self.assertEqual(packet["recommended_status"], "needs_real_optix_artifact")
        self.assertFalse(packet["required_records_ok"])

    def test_parity_failure_blocks_review(self) -> None:
        payload = _payload(host_ok=True, native_ok=False)
        packet = goal864.build_packet(payload)
        self.assertEqual(packet["recommended_status"], "needs_real_optix_artifact")

    def test_full_parity_with_postgis_is_ready_for_review(self) -> None:
        packet = goal864.build_packet(_payload(host_ok=True, native_ok=True, include_postgis=True, postgis_ok=True))
        self.assertEqual(packet["recommended_status"], "ready_for_review")
        self.assertTrue(packet["required_records_ok"])
        self.assertTrue(packet["required_parity_ok"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_json = Path(tmp) / "input.json"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            input_json.write_text(json.dumps(_payload()), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal864_segment_polygon_gate_review_packet.py",
                    "--input-json",
                    str(input_json),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": "src:."},
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["recommended_status"], "needs_real_optix_artifact")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
