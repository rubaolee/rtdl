import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.embree_runtime import EMBREE_REQUIRED_SYMBOLS


class Goal467ExternalReportResponseTest(unittest.TestCase):
    def test_public_graph_exports_include_csr_constructor(self) -> None:
        graph = rt.csr_graph(row_offsets=(0, 1, 1), column_indices=(1,))
        self.assertEqual(graph.vertex_count, 2)
        self.assertTrue(callable(rt.validate_csr_graph))
        self.assertIn("csr_graph", rt.__all__)
        self.assertIn("validate_csr_graph", rt.__all__)

    def test_embree_required_symbols_cover_windows_audit_exports(self) -> None:
        self.assertIn("rtdl_embree_run_fixed_radius_neighbors", EMBREE_REQUIRED_SYMBOLS)
        self.assertIn("rtdl_embree_run_bfs_expand", EMBREE_REQUIRED_SYMBOLS)
        self.assertIn("rtdl_embree_run_triangle_probe", EMBREE_REQUIRED_SYMBOLS)
        self.assertIn("rtdl_embree_db_dataset_create_columnar", EMBREE_REQUIRED_SYMBOLS)


if __name__ == "__main__":
    unittest.main()
