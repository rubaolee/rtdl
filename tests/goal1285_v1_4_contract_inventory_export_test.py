from __future__ import annotations

import json
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import goal1285_v1_4_contract_inventory_export as exporter


class Goal1285V14ContractInventoryExportTest(unittest.TestCase):
    def test_payload_summarizes_active_and_frozen_contracts(self) -> None:
        payload = exporter.build_inventory_payload()

        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["public_wording_authorized"])
        self.assertEqual(payload["active_v1_4_backends"], ["embree", "optix"])
        self.assertEqual(payload["frozen_before_v2_1_backends"], ["vulkan", "hiprt", "apple_rt"])
        self.assertEqual(payload["contract_count"], 20)
        self.assertEqual(payload["active_contract_count"], 8)
        self.assertEqual(payload["frozen_contract_count"], 12)

    def test_main_writes_json_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "inventory.json"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(exporter.main(["--output-json", str(output)]), 0)

            payload = json.loads(output.read_text(encoding="utf-8"))
            printed = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "valid")
            self.assertEqual(printed["status"], "valid")
            self.assertEqual(payload["contract_count"], 20)


if __name__ == "__main__":
    unittest.main()
