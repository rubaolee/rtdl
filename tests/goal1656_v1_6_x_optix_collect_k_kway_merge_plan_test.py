import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1656_v1_6_x_optix_collect_k_kway_merge_plan.py"


class Goal1656OptixCollectKKWayMergePlanTest(unittest.TestCase):
    def test_topology_model_targets_merge_chain_reduction(self) -> None:
        import scripts.goal1656_v1_6_x_optix_collect_k_kway_merge_plan as plan

        binary = plan.merge_topology(input_segments=128, segment_capacity=2048, fan_in=2)
        four_way = plan.merge_topology(input_segments=128, segment_capacity=2048, fan_in=4)
        eight_way = plan.merge_topology(input_segments=128, segment_capacity=2048, fan_in=8)

        self.assertEqual(binary.segment_chain, [128, 64, 32, 16, 8, 4, 2, 1])
        self.assertEqual(binary.estimated_kernel_launches, 27)
        self.assertEqual(four_way.segment_chain, [128, 32, 8, 2, 1])
        self.assertLess(four_way.merge_levels, binary.merge_levels)
        self.assertLess(four_way.estimated_kernel_launches, binary.estimated_kernel_launches)
        self.assertEqual(eight_way.segment_chain, [128, 16, 2, 1])

    def test_reference_contract_sorts_dedupes_and_bounds_capacity(self) -> None:
        import scripts.goal1656_v1_6_x_optix_collect_k_kway_merge_plan as plan

        segments = [
            [(1, 10), (2, 20), (4, 40)],
            [(1, 10), (3, 30), (7, 70)],
            [(0, 0), (4, 40), (8, 80)],
            [(2, 20), (5, 50), (9, 90)],
        ]

        self.assertEqual(
            plan.kway_merge_reference(segments),
            [(0, 0), (1, 10), (2, 20), (3, 30), (4, 40), (5, 50), (7, 70), (8, 80), (9, 90)],
        )
        self.assertEqual(
            plan.kway_merge_reference(segments, capacity=5),
            [(0, 0), (1, 10), (2, 20), (3, 30), (4, 40)],
        )

    def test_cli_writes_claim_bounded_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "goal1656.json"
            md_out = Path(tmp) / "goal1656.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
            )

            payload = json.loads(json_out.read_text(encoding="utf-8"))
            text = md_out.read_text(encoding="utf-8")

        self.assertEqual(payload["status"], "kway_merge_plan_recorded")
        self.assertIs(payload["claim_boundary"]["gpu_timing_recorded"], False)
        self.assertIn("`kway_merge_native_probe_prepared`", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("not enabled by", text)


if __name__ == "__main__":
    unittest.main()
