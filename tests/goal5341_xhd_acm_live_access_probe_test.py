import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "probe_xhd_acm_supplement_live_access.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5341_acm_supplement_live_access_probe.json"
)


class Goal5341XhdAcmLiveAccessProbeTest(unittest.TestCase):
    def test_summary_records_current_claim_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.goal5341.acm_supplement_live_access_probe.v1")
        self.assertEqual(summary["exit_label"], "acm_supplement_live_access_probe_ready__current_environment_still_not_exact_input")
        self.assertFalse(summary["pod_usage"]["used"])
        for key in [
            "acm_supplement_inspected",
            "zip_contents_inspected",
            "same_input_gate_passed",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_paper_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
        ]:
            self.assertFalse(summary["claim_boundary"][key])

    def test_script_can_write_json_without_network_when_url_is_unreachable_localhost(self):
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "probe.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--url",
                    "http://127.0.0.1:9/ics26-106.zip",
                    "--timeout-sec",
                    "0.25",
                    "--output",
                    str(out),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["artifact_name"], "ics26-106.zip")
            self.assertEqual(payload["classification"], "acm_supplement_not_downloadable_from_current_environment")
            self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])

    def test_cookie_file_must_be_single_header_line(self):
        with tempfile.TemporaryDirectory() as td:
            cookie = pathlib.Path(td) / "cookie.txt"
            cookie.write_text("a=b\nc=d\n", encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--url",
                    "http://127.0.0.1:9/ics26-106.zip",
                    "--cookie-file",
                    str(cookie),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("single Cookie header", proc.stderr)


if __name__ == "__main__":
    unittest.main()
