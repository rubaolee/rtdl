import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "xhd_memory_accounting.py"
)
EXACT_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json"
)
FAST_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("xhd_memory_accounting", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5273MemoryAccountingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mem = _load_module()

    def test_exact_witness_route_exposes_estimated_grid_and_zero_worklist(self):
        payload = json.loads(EXACT_ARTIFACT.read_text(encoding="utf-8"))
        accounting = self.mem.rtdl_memory_accounting_from_hd_exec_payload(payload)
        self.assertEqual(accounting["route_label"], "cell-mbr-exact-witness")
        self.assertEqual(accounting["frontier_row_count"], 0)
        self.assertIsNone(accounting["frontier_row_capacity"])
        self.assertEqual(accounting["author_mapped_fields"]["WL"]["bytes"], 0)
        self.assertGreater(accounting["author_mapped_fields"]["Grid"]["bytes"], 0)
        self.assertGreater(accounting["author_mapped_fields"]["MBRs B"]["bytes"], 0)

    def test_fast_scalar_route_accounts_allocated_frontier_capacity(self):
        payload = json.loads(FAST_ARTIFACT.read_text(encoding="utf-8"))
        route = payload["RTDL"]["route"]["directed_a_to_b"]
        accounting = self.mem.rtdl_memory_accounting_from_hd_exec_payload(payload)
        wl = accounting["author_mapped_fields"]["WL"]
        self.assertEqual(accounting["route_label"], "cell-mbr-fast-scalar")
        self.assertEqual(route["frontier_row_capacity"], 3501160)
        self.assertEqual(
            wl["bytes"],
            3501160 * 8 * 8,
        )
        self.assertEqual(
            wl["status"],
            "estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue",
        )
        self.assertIn("not the author's Figure 11 WL denominator", wl["method"])

    def test_unavailable_author_fields_are_not_silent_zeroes(self):
        payload = json.loads(FAST_ARTIFACT.read_text(encoding="utf-8"))
        accounting = self.mem.rtdl_memory_accounting_from_hd_exec_payload(payload)
        self.assertIsNone(accounting["author_mapped_fields"]["BVH"]["bytes"])
        self.assertIn("unavailable", accounting["author_mapped_fields"]["BVH"]["status"])
        self.assertIsNone(accounting["author_mapped_fields"]["WL Heavy Peak"]["bytes"])
        self.assertIn(
            "unavailable",
            accounting["author_mapped_fields"]["WL Heavy Peak"]["status"],
        )

    def test_claim_boundary_forbids_figure11_parity_claims(self):
        payload = json.loads(EXACT_ARTIFACT.read_text(encoding="utf-8"))
        accounting = self.mem.rtdl_memory_accounting_from_hd_exec_payload(payload)
        for key, value in accounting["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
