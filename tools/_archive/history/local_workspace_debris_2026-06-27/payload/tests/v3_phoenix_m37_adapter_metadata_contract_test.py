import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"


def _function_body(source: str, function_name: str) -> str:
    marker = f"def {function_name}("
    start = source.index(marker)
    next_start = source.find("\ndef ", start + len(marker))
    if next_start == -1:
        next_start = len(source)
    return source[start:next_start]


class V3PhoenixM37AdapterMetadataContractTest(unittest.TestCase):
    def test_grouped_vector_sum_real_adapter_preserves_row_and_group_counts(self):
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        prepare_body = _function_body(
            source,
            "prepare_grouped_vector_sum_2d_partner_columns_session",
        )
        run_body = _function_body(
            source,
            "run_grouped_vector_sum_2d_partner_columns_session",
        )

        self.assertIn('"group_count": group_count', prepare_body)
        self.assertIn('"row_count": row_count', prepare_body)
        self.assertIn('"output_columns_reused": True', prepare_body)
        self.assertIn('"per_run_neutral_handoff_validation_used": False', prepare_body)
        self.assertIn('metadata = dict(prepared_session["metadata"])', run_body)
        self.assertIn('"adapter": "run_grouped_vector_sum_2d_partner_columns_session"', run_body)
        self.assertIn('"prepared_session_reused": True', run_body)
        self.assertIn('"output_columns_reused": True', run_body)
        self.assertIn('"per_run_neutral_handoff_validation_used": False', run_body)

    def test_component_union_real_adapter_has_separate_union_and_signature_entrypoints(self):
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        union_body = _function_body(
            source,
            "radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns",
        )
        signature_body = _function_body(
            source,
            "radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns",
        )

        self.assertIn("return prepared.run(", union_body)
        self.assertNotIn("run_component_signature", union_body)
        self.assertIn("return prepared.run_component_signature(", signature_body)


if __name__ == "__main__":
    unittest.main()
