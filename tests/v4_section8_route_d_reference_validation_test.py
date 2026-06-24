from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "v4_section8_route_d_reference_validation.py"
REFERENCE = ROOT / "future" / "v4" / "reference" / "route_d_fixed_radius_count_threshold_optix.cpp"
PROTOCOL = ROOT / "future" / "v4" / "rtdl_v4_0_section8_route_d_handwritten_optix_protocol_2026-06-24.md"


class V4Section8RouteDReferenceValidationTest(unittest.TestCase):
    def test_dry_run_records_independence_boundary(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(HARNESS), "--dry-run", "--copies", "8192"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual("dry_run", payload["status"])
        self.assertEqual("v4_section8_route_d_handwritten_optix_reference", payload["protocol"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["near_handwritten_optix_claim_authorized"])
        self.assertFalse(payload["independence_contract"]["imports_rtdsl"])
        self.assertFalse(payload["independence_contract"]["links_librtdl_optix"])
        self.assertFalse(payload["independence_contract"]["calls_rtdl_optix_symbols"])
        self.assertTrue(payload["independence_contract"]["standalone_cuda_driver_optix"])

    def test_reference_source_is_not_linked_to_rtdl_runtime(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        forbidden = (
            "rtdsl",
            "librtdl_optix",
            "rtdl_optix_",
            "run_app",
            "PreparedOutlierDetectionSession",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, text)
        self.assertIn("optixLaunch", text)
        self.assertIn("__raygen__fixed_radius_count_threshold", text)
        self.assertIn("make_fixture", text)

    def test_protocol_keeps_route_d_non_release(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("no link to `librtdl_optix.so`", text)
        self.assertIn("no call to any `rtdl_optix_*` symbol", text)
        self.assertIn("Near hand-written OptiX wording remains unauthorized", text)
        self.assertIn("externally reviewed", text)


if __name__ == "__main__":
    unittest.main()
