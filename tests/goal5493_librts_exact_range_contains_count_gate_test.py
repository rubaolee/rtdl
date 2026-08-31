from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_exact_range_contains_count_gate",
    APP / "run_exact_range_contains_count_gate.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class _Prepared:
    def count(self, *, box_queries, operation):
        return {
            "backend": "optix",
            "counts": {"range_contains": 1},
            "run_phases": {"query_aabb_index_2d_sec": 0.02},
            "rt_core_accelerated": True,
            "native_engine_customization": False,
        }

    def close(self):
        pass


class Goal5493LibrtsExactRangeContainsCountGateTest(unittest.TestCase):
    def test_gate_preserves_exact_count_and_claim_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            geometry = root / "geometry.wkt"
            query = root / "query.wkt"
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n", encoding="utf-8")
            query.write_text("POLYGON ((0 0, 0.5 0, 0 0.5, 0 0))\n", encoding="utf-8")
            extraction = {
                "claim_boundary": {"archive_subset_extracted": True},
                "extraction": {"final_path": str(root), "selected_members": []},
            }
            extraction["extraction"]["selected_members"] = [
                {"relative_path": "geometry.wkt", "size_bytes": geometry.stat().st_size, "sha256": MODULE._sha256(geometry)},
                {"relative_path": "query.wkt", "size_bytes": query.stat().st_size, "sha256": MODULE._sha256(query)},
            ]
            author = {"geometry_count": 1, "query_count": 1, "result_count": 1}
            with (
                mock.patch.object(MODULE, "run_author_range_contains", return_value=(author, "", ["author"])),
                mock.patch.object(MODULE.rt, "prepare_aabb_index_2d_columns", return_value=_Prepared()),
            ):
                result = MODULE.run_gate(
                    author_binary=root / "author",
                    ae_root=root,
                    geometry_path=geometry,
                    query_path=query,
                    serialize_dir=root / "serialize",
                    archive_result={"claim_boundary": {"archive_verified": True}},
                    extraction_result=extraction,
                )
        self.assertTrue(result["matched"])
        self.assertFalse(result["claim_boundary"]["pointwise_containment_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])


if __name__ == "__main__":
    unittest.main()
