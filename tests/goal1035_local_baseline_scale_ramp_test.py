from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


class Goal1035LocalBaselineScaleRampTest(unittest.TestCase):
    def test_with_copies_rewrites_only_existing_copies_flag(self) -> None:
        module = __import__("scripts.goal1035_local_baseline_scale_ramp", fromlist=["_with_copies"])
        command = ["python3", "app.py", "--backend", "cpu", "--copies", "20000"]
        self.assertEqual(
            module._with_copies(command, 500),
            ["python3", "app.py", "--backend", "cpu", "--copies", "500"],
        )
        no_copies = ["python3", "app.py", "--backend", "cpu"]
        self.assertEqual(module._with_copies(no_copies, 500), no_copies)

    def test_backend_extracts_backend_flag(self) -> None:
        module = __import__("scripts.goal1035_local_baseline_scale_ramp", fromlist=["_backend"])
        self.assertEqual(module._backend(["python3", "app.py", "--backend", "embree"]), "embree")
        self.assertEqual(module._backend(["python3", "app.py"]), "unknown")

    def test_build_payload_classifies_failures(self) -> None:
        module = __import__("scripts.goal1035_local_baseline_scale_ramp", fromlist=["build_payload"])
        payload = module.build_payload(
            [
                {"status": "ok"},
                {"status": "optional_dependency_unavailable"},
            ],
            copies_list=[50],
            timeout_sec=1.0,
        )
        self.assertEqual(payload["status"], "ok_with_optional_dependency_gaps")
        failed = module.build_payload([{"status": "timeout"}], copies_list=[50], timeout_sec=1.0)
        self.assertEqual(failed["status"], "needs_attention")

    def test_write_outputs_updates_json_and_markdown(self) -> None:
        module = __import__("scripts.goal1035_local_baseline_scale_ramp", fromlist=["write_outputs"])
        row = {
            "app": "outlier_detection",
            "copies": 50,
            "backend": "cpu",
            "status": "ok",
            "elapsed_sec": 0.1,
            "json_summary": {"app": "outlier_detection", "backend": "cpu", "copies": 50},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "out.json"
            output_md = Path(tmpdir) / "out.md"
            module.write_outputs(
                [row],
                copies_list=[50],
                timeout_sec=1.0,
                output_json=output_json,
                output_md=output_md,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["row_count"], 1)
            self.assertIn("does not authorize speedup claims", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
