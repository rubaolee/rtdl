from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation.py"


class V4ClosestHitGroupedArgminDeviceFrontdoorValidationTest(unittest.TestCase):
    def test_dry_run_records_scope_without_requiring_gpu(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry_run.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--ray-count",
                    "8192",
                    "--json-out",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual("dry_run", payload["status"])
        self.assertEqual((8192,), tuple(payload["parameters"]["ray_counts"]))
        self.assertFalse(payload["claim_boundary"]["release_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_v4_speedup_claim_authorized"])
        self.assertEqual(
            "v4_closest_hit_grouped_argmin_3d_device_arrays",
            payload["claim_boundary"]["measured_surface"],
        )
        self.assertIn("correctness host reads are outside timed repeats", payload["timing_boundary"])

    def test_script_keeps_device_frontdoor_and_legacy_materialization_separate(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"device_array_frontdoor"', source)
        self.assertIn('"legacy_host_materialize"', source)
        self.assertIn('"host_materialization_in_hot_path": False', source)
        self.assertIn('"host_materialization_in_hot_path": True', source)
        self.assertIn('"tier3_callback_claim_authorized": False', source)


if __name__ == "__main__":
    unittest.main()
