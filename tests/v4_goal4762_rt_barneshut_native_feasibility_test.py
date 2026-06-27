from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    V4_RT_BARNESHUT_EXISTING_2D_AGGREGATE_TREE_SYMBOLS,
    V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED,
    V4RtBarnesHutNativeRouteUnavailable,
    inspect_v4_rt_barneshut_native_feasibility,
    run_v4_rt_barneshut_native_author_route,
    validate_v4_rt_barneshut_native_feasibility,
)


class V4Goal4762RtBarnesHutNativeFeasibilityTest(unittest.TestCase):
    def test_native_author_route_gate_preserves_claim_boundaries(self) -> None:
        feasibility = inspect_v4_rt_barneshut_native_feasibility(ROOT)
        validate_v4_rt_barneshut_native_feasibility(feasibility)

        self.assertIn(
            feasibility.status,
            {
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED,
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED,
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
            },
        )
        for symbol in V4_RT_BARNESHUT_EXISTING_2D_AGGREGATE_TREE_SYMBOLS:
            self.assertTrue(feasibility.existing_2d_aggregate_tree_symbols[symbol])
        self.assertFalse(
            feasibility.claim_boundary["existing_2d_aggregate_tree_route_is_author_equivalent"]
        )
        self.assertFalse(feasibility.claim_boundary["v2_v3_v4_author_speed_table_authorized"])
        self.assertIn("3d_float32_position_columns_x_y_z", feasibility.required_dataflow)
        self.assertIn("author_force_law_checksum_parity", feasibility.required_dataflow)

    def test_native_author_route_fails_closed_instead_of_falling_back(self) -> None:
        with self.assertRaises(V4RtBarnesHutNativeRouteUnavailable) as raised:
            run_v4_rt_barneshut_native_author_route()

        message = str(raised.exception)
        self.assertIn("Native V4 RT-BarnesHut", message)
        self.assertNotIn("aggregate_tree_fused_weighted_vector_sum_2d", message)

    def test_probe_writes_machine_readable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "native_feasibility.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "v4_rt_barneshut_native_feasibility_probe.py"),
                    "--source-root",
                    str(ROOT),
                    "--output",
                    str(output),
                ],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

            self.assertEqual(payload["goal"], "Goal4762")
            self.assertIn(
                payload["status"],
                {
                    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED,
                    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED,
                    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
                    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
                },
            )
            self.assertFalse(payload["claim_boundary"]["old_2d_rtdl_workflow_may_be_divided_by_author_binary"])
            if payload["status"] == V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED:
                self.assertEqual(
                    tuple(payload["missing_native_author_symbols"]),
                    V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS,
                )


if __name__ == "__main__":
    unittest.main()
