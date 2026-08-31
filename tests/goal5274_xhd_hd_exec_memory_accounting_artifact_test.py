import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5274_hd_exec_memory_accounting_attached_example_2026-07-09.json"
)


class Goal5274XhdHdExecMemoryAccountingArtifactTest(unittest.TestCase):
    def test_attached_artifact_is_status_bearing_not_figure11_reproduction(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        marker = payload["RTDL"]["memory_accounting_attachment_artifact"]
        self.assertEqual(
            marker["status"],
            "hd_exec_compatible_running_memory_status_attached__figure11_not_reproduced",
        )
        for key in (
            "new_route_execution_claimed",
            "figure11_reproduced",
            "author_memory_parity_claimed",
            "exact_gpu_allocator_measurement_claimed",
        ):
            self.assertFalse(marker["claim_boundary"][key], key)

        memory = payload["Running"]["Repeats"][0]["Memory"]
        self.assertEqual(memory["Status"], "status_bearing_rtdl_memory_accounting_attached")
        self.assertIn("not the author's Figure 11 Memory schema", memory["Semantics"])
        accounting = memory["Accounting"]
        self.assertEqual(accounting["schema"], "rtdl.paper_reproduction.xhd.rtdl_memory_accounting.v1")
        self.assertIsNone(accounting["author_mapped_fields"]["BVH"]["bytes"])
        self.assertGreater(accounting["author_mapped_fields"]["Grid"]["bytes"], 0)
        self.assertFalse(accounting["claim_boundary"]["figure11_reproduced"])


if __name__ == "__main__":
    unittest.main()
