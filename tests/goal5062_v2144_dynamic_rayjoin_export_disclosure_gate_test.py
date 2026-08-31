from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_DOCS = ROOT / "history" / "internal_docs"
SCRIPT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"
REPORT = INTERNAL_DOCS / "goal5062_v2_14_4_dynamic_rayjoin_export_disclosure_gate_2026-07-06.md"
CALL = INTERNAL_DOCS / "call_for_review_goal5062_v2_14_4_dynamic_rayjoin_export_disclosure_gate_2026-07-06.md"
BOUNDARY_REPORTS = (
    INTERNAL_DOCS / "goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md",
    INTERNAL_DOCS / "goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md",
    INTERNAL_DOCS / "goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md",
    REPORT,
)


class Goal5062V2144DynamicRayjoinExportDisclosureGateTest(unittest.TestCase):
    def test_dynamic_rayjoin_export_set_is_disclosed(self) -> None:
        dynamic = sorted(name for name in rt.__all__ if "rayjoin" in name.lower())
        self.assertEqual(17, len(dynamic))
        self.assertIn("PreparedOptixRayjoinCdbPointLocation2D", dynamic)
        self.assertIn("RayJoinPublicAsset", dynamic)
        self.assertIn("rayjoin_public_assets", dynamic)

        for path in BOUNDARY_REPORTS:
            text = path.read_text(encoding="utf-8")
            for name in dynamic:
                self.assertIn(name, text, path.name)
            self.assertIn("not new v2.14.4 public generic API", text)

    def test_preflight_reports_dynamic_export_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preflight.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--allow-blocked",
                    "--output-json",
                    str(output),
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))

        check = next(item for item in payload["checks"] if item["id"] == "legacy_rayjoin_public_exports_disclosed")
        self.assertEqual("pass", check["status"])
        self.assertEqual(
            sorted((name for name in rt.__all__ if "rayjoin" in name.lower()), key=str.lower),
            check["exports"],
        )
        self.assertEqual([], check["missing_expected_exports_from_rtdsl_all"])
        self.assertEqual([], check["unexpected_rayjoin_exports_from_rtdsl_all"])

    def test_report_and_call_document_bf1_resolution(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call = CALL.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("BF-1", report)
        self.assertIn("seventeen RayJoin-named public", report)
        self.assertIn("approve_goal5062_dynamic_rayjoin_export_disclosure_gate", call)
        self.assertIn("EXPECTED_RAYJOIN_PUBLIC_EXPORTS", script)
        self.assertIn("_rayjoin_exports_from_init_all", script)


if __name__ == "__main__":
    unittest.main()
