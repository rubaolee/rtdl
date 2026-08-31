from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5160ActiveFrontierRowsTest(unittest.TestCase):
    def test_native_abi_exposes_emit_pruned_rows_flag(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        partner = (ROOT / "src/rtdsl/partner_continuations.py").read_text(encoding="utf-8")

        self.assertIn("uint32_t emit_pruned_rows", prelude)
        self.assertIn("uint32_t emit_pruned_rows", api)
        self.assertIn("uint32_t emit_pruned_rows", workloads)
        self.assertIn("emit_pruned_rows: bool = True", runtime)
        self.assertIn("emit_pruned_rows: bool = True", partner)
        self.assertIn("kind == 3 && params.emit_pruned_rows == 0u", workloads)

    def test_xhd_streaming_route_requests_active_rows_only(self) -> None:
        script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")
        native_call = script.index("rt.cell_mbr_nearest_frontier_native_3d_optix_columns")
        native_block_end = script.index("elif backend == \"numpy\"", native_call)
        native_block = script[native_call:native_block_end]
        self.assertIn("emit_pruned_rows=False", native_block)
        self.assertIn("return_split_frontiers=False", native_block)

    def test_active_frontier_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_active_frontier_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5160 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        self.assertFalse(payload["author_performance_parity_claimed"])
        sample1024 = {case["case"]: case for case in payload["cases"]}["sample1024"]
        self.assertTrue(sample1024["matched"])
        self.assertEqual(sample1024["rtdl"]["validation_mode"], "author-only")
        self.assertLess(sample1024["rtdl"]["route_sec_median"], 0.09)
        self.assertLess(sample1024["rtdl"]["directed_a_to_b"]["frontier_row_count"], 5000)
        self.assertLess(sample1024["rtdl"]["directed_b_to_a"]["frontier_row_count"], 5000)
        self.assertGreater(sample1024["rtdl"]["directed_a_to_b"]["continuation_candidate_distance_evaluations"], 10000)
        self.assertGreater(sample1024["rtdl"]["directed_b_to_a"]["continuation_candidate_distance_evaluations"], 10000)


if __name__ == "__main__":
    unittest.main()
