from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_rtdl_hd_exec.py"
RESULTS = APP_DIR / "results"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_b.wkt"


def _load_runner():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_hd_exec_goal5274", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5274XhdHdExecMemoryAccountingIntegrationTest(unittest.TestCase):
    def test_cell_mbr_payload_gets_status_bearing_running_memory(self) -> None:
        runner = _load_runner()
        payload_path = RESULTS / "xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json"
        payload = json.loads(payload_path.read_text(encoding="utf-8"))

        runner._attach_memory_accounting_if_requested(payload, include_memory_accounting=True)

        memory = payload["Running"]["Repeats"][0]["Memory"]
        self.assertEqual(
            memory["Schema"],
            "rtdl.paper_reproduction.xhd.rtdl_memory_accounting.running_repeat.v1",
        )
        self.assertEqual(memory["Status"], "status_bearing_rtdl_memory_accounting_attached")
        self.assertIn("not the author's Figure 11 Memory schema", memory["Semantics"])
        self.assertIs(memory["Accounting"], payload["RTDL"]["memory_accounting"])

        accounting = memory["Accounting"]
        self.assertEqual(accounting["schema"], "rtdl.paper_reproduction.xhd.rtdl_memory_accounting.v1")
        fields = accounting["author_mapped_fields"]
        self.assertEqual(
            fields["BVH"]["status"],
            "unavailable_opaque_native_acceleration_memory_not_reported",
        )
        self.assertIsNone(fields["BVH"]["bytes"])
        self.assertGreater(fields["Grid"]["bytes"], 0)
        self.assertGreater(fields["MBRs B"]["bytes"], 0)
        self.assertFalse(payload["RTDL"]["claim_boundary"]["figure11_reproduction_claimed"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["author_memory_parity_claimed"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["exact_gpu_allocator_measurement_claimed"])

    def test_public_columnar_route_memory_accounting_is_explicitly_unavailable(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "public_memory.json"
            rc = runner.main(
                [
                    "-input1",
                    str(FIXTURE_A),
                    "-input2",
                    str(FIXTURE_B),
                    "-n_dims",
                    "2",
                    "-input_type",
                    "wkt",
                    "-variant",
                    "rt",
                    "-execution",
                    "cpu",
                    "-json",
                    str(out),
                    "--rtdl-route",
                    "public-columnar",
                    "--include-memory-accounting",
                ]
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        accounting = payload["Running"]["Repeats"][0]["Memory"]["Accounting"]
        self.assertEqual(accounting["status"], "memory_accounting_unavailable_for_selected_route")
        self.assertEqual(accounting["route_label"], "public-columnar")
        for field in accounting["author_mapped_fields"].values():
            self.assertIsNone(field["bytes"])
            self.assertIn("unavailable", field["status"])
        self.assertEqual(accounting["estimated_total_accounted_bytes_excluding_unavailable"], 0)
        self.assertFalse(accounting["claim_boundary"]["figure11_reproduced"])


if __name__ == "__main__":
    unittest.main()
