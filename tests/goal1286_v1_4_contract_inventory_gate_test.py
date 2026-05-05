from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal1285_v1_4_contract_inventory_export as exporter
from scripts import goal1286_v1_4_contract_inventory_gate as gate


class Goal1286V14ContractInventoryGateTest(unittest.TestCase):
    def test_gate_accepts_current_export_payload(self) -> None:
        result = gate.validate_inventory_payload(exporter.build_inventory_payload())

        self.assertTrue(result["valid"])
        self.assertEqual(result["failure_count"], 0)
        self.assertEqual(result["checked_contract_count"], 20)

    def test_gate_rejects_public_wording_promotion(self) -> None:
        payload = exporter.build_inventory_payload()
        payload["public_wording_authorized"] = True

        result = gate.validate_inventory_payload(payload)

        self.assertFalse(result["valid"])
        self.assertIn("public_wording_authorized must remain false", result["failures"])

    def test_gate_rejects_frozen_backend_promotion(self) -> None:
        payload = exporter.build_inventory_payload()
        mutated = copy.deepcopy(payload)
        for contract in mutated["contracts"]:
            if contract["backend"] == "vulkan":
                contract["active_v1_4_backend"] = True
                break

        result = gate.validate_inventory_payload(mutated)

        self.assertFalse(result["valid"])
        self.assertTrue(any("vulkan must remain inactive" in failure for failure in result["failures"]))

    def test_main_writes_gate_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            inventory = Path(tmp) / "inventory.json"
            output = Path(tmp) / "gate.json"
            inventory.write_text(json.dumps(exporter.build_inventory_payload()), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(gate.main([str(inventory), "--output-json", str(output)]), 0)

            result = json.loads(output.read_text(encoding="utf-8"))
            printed = json.loads(stdout.getvalue())
            self.assertTrue(result["valid"])
            self.assertTrue(printed["valid"])


if __name__ == "__main__":
    unittest.main()
