from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2625SegmentedRowStreamTest(unittest.TestCase):
    def test_contract_exports_generic_segmented_row_stream(self) -> None:
        contract = rt.segmented_row_stream_contract()

        self.assertEqual(contract["primitive"], "SEGMENTED_ROW_STREAM")
        self.assertEqual(contract["alias"], "CHUNKED_ROW_CONTINUATION")
        self.assertEqual(contract["version"], "rtdl.segmented_row_stream.v1")
        self.assertEqual(contract["status"], "internal_substrate")
        self.assertIn("fail_closed_no_partial_result", contract["overflow_policy"])
        self.assertIn("emit_segmented_row_stream", rt.__all__)
        self.assertIn("SegmentedRowPage", rt.__all__)

    def test_stream_pages_reconstruct_exact_rows_with_tokens(self) -> None:
        rows = ((0, 10), (1, 11), (2, 12), (3, 13), (4, 14))

        stream = rt.emit_segmented_row_stream(
            rows,
            row_schema=("query_id", "indexed_id"),
            page_capacity=2,
            stream_id="pairs",
        )

        self.assertEqual(stream.total_rows, 5)
        self.assertEqual(len(stream.pages), 3)
        self.assertEqual(stream.pages[0].next_token, "pairs:2")
        self.assertEqual(stream.pages[1].next_token, "pairs:4")
        self.assertIsNone(stream.pages[2].next_token)
        self.assertEqual(rt.reconstruct_segmented_row_stream(stream.pages), rows)

        validation = rt.validate_segmented_row_pages(stream.pages)
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["total_rows"], 5)
        self.assertTrue(validation["complete_candidate_coverage"])

    def test_single_page_api_resumes_from_continuation_token(self) -> None:
        rows = ((0, 10), (1, 11), (2, 12), (3, 13))
        first = rt.emit_segmented_row_page(
            rows,
            row_schema=("query_id", "indexed_id"),
            page_capacity=2,
            stream_id="resume",
        )
        second = rt.emit_segmented_row_page(
            rows,
            row_schema=("query_id", "indexed_id"),
            page_capacity=2,
            stream_id="resume",
            continuation_token=first.next_token,
        )

        self.assertEqual(first.rows, ((0, 10), (1, 11)))
        self.assertEqual(second.rows, ((2, 12), (3, 13)))
        self.assertFalse(first.complete_candidate_coverage)
        self.assertTrue(second.complete_candidate_coverage)
        self.assertEqual(rt.reconstruct_segmented_row_stream((first, second)), rows)

    def test_windowed_stream_cannot_be_mistaken_for_complete_output(self) -> None:
        rows = tuple((index, index + 100) for index in range(6))

        stream = rt.emit_segmented_row_stream(
            rows,
            row_schema=("left_id", "right_id"),
            page_capacity=2,
            max_pages=2,
        )

        self.assertFalse(stream.complete_candidate_coverage)
        self.assertEqual(stream.next_token, "rtdl_segmented_row_stream:4")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            rt.reconstruct_segmented_row_stream(stream.pages)
        self.assertEqual(
            rt.reconstruct_segmented_row_stream(stream.pages, require_complete=False),
            rows[:4],
        )

    def test_empty_stream_is_complete_and_reconstructs_to_no_rows(self) -> None:
        stream = rt.emit_segmented_row_stream(
            rows=(),
            row_schema=("query_id", "indexed_id"),
            page_capacity=4,
            stream_id="empty",
        )

        self.assertTrue(stream.complete_candidate_coverage)
        self.assertEqual(stream.total_rows, 0)
        self.assertEqual(len(stream.pages), 1)
        self.assertEqual(rt.reconstruct_segmented_row_stream(stream.pages), ())
        self.assertEqual(rt.validate_segmented_row_pages(stream.pages)["total_rows"], 0)

    def test_total_capacity_overflow_fails_closed_before_returning_pages(self) -> None:
        rows = tuple((index, index + 1) for index in range(4))

        with self.assertRaisesRegex(
            rt.SegmentedRowStreamOverflowError,
            "failure_mode=fail_closed_overflow .*partial_result_returned=False",
        ):
            rt.emit_segmented_row_stream(
                rows,
                row_schema=("source_id", "target_id"),
                page_capacity=2,
                total_row_capacity=3,
            )

    def test_row_schema_and_page_validation_reject_bad_streams(self) -> None:
        with self.assertRaisesRegex(ValueError, "row width"):
            rt.emit_segmented_row_stream(
                rows=((1, 2, 3),),
                row_schema=("a", "b"),
                page_capacity=1,
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            rt.emit_segmented_row_stream(
                rows=((1, 2),),
                row_schema=("id", "id"),
                page_capacity=1,
            )

        page = rt.emit_segmented_row_page(
            rows=((0, 10), (1, 11)),
            row_schema=("query_id", "indexed_id"),
            page_capacity=1,
            stream_id="bad",
        )
        bad_page = rt.SegmentedRowPage(
            stream_id="bad",
            page_index=1,
            row_offset=3,
            row_schema=page.row_schema,
            rows=((1, 11),),
            page_capacity=1,
            next_token=None,
            complete_candidate_coverage=True,
        )
        with self.assertRaisesRegex(ValueError, "row_offset"):
            rt.validate_segmented_row_pages((page, bad_page))

    def test_token_helpers_reject_cross_stream_and_malformed_tokens(self) -> None:
        self.assertEqual(rt.make_segmented_row_token("stream", 4), "stream:4")
        self.assertEqual(
            rt.parse_segmented_row_token("stream:4", stream_id="stream"),
            4,
        )

        with self.assertRaisesRegex(ValueError, "stream_id"):
            rt.make_segmented_row_token("bad:stream", 0)
        with self.assertRaisesRegex(ValueError, "does not belong"):
            rt.parse_segmented_row_token("other:4", stream_id="stream")
        with self.assertRaisesRegex(ValueError, "integer"):
            rt.parse_segmented_row_token("stream:not-an-int", stream_id="stream")
        with self.assertRaisesRegex(ValueError, "non-negative"):
            rt.parse_segmented_row_token("stream:-1", stream_id="stream")
        with self.assertRaisesRegex(ValueError, "align with page_capacity"):
            rt.emit_segmented_row_page(
                rows=((0, 10), (1, 11), (2, 12)),
                row_schema=("query_id", "indexed_id"),
                page_capacity=2,
                stream_id="stream",
                continuation_token="stream:1",
            )

    def test_segmented_stream_composes_with_existing_aabb_rows(self) -> None:
        payload = rt.aabb_intersection_pair_rows_2d(
            indexed_boxes=((0.0, 0.0, 1.0, 1.0), (2.0, 0.0, 3.0, 1.0)),
            query_boxes=((0.25, 0.0, 0.75, 1.0), (2.25, 0.0, 2.75, 1.0)),
            indexed_ids=(100, 101),
            query_ids=(200, 201),
            resolution=8,
        )

        stream = rt.emit_segmented_row_stream(
            payload["candidate_id_rows"],
            row_schema=payload["row_schema"],
            page_capacity=1,
            stream_id="aabb_pairs",
        )

        self.assertEqual(stream.total_rows, payload["valid_count"])
        self.assertEqual(
            rt.reconstruct_segmented_row_stream(stream.pages),
            payload["candidate_id_rows"],
        )
        self.assertFalse(payload["native_engine_customization"])

    def test_hierarchy_and_docs_record_goal2625_contract(self) -> None:
        node = rt.find_primitive_hierarchy_node("continuation.segmented_chunked_rows")
        self.assertEqual(node.status, "internal_substrate")
        self.assertIn("row_pages", node.outputs)

        catalog = (ROOT / "docs" / "rtdl_primitive_catalog.md").read_text(
            encoding="utf-8"
        )
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal2625_segmented_row_stream_contract_2026-05-26.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reports"
            / "goal2625_segmented_row_stream_3ai_consensus_2026-05-26.md"
        ).read_text(encoding="utf-8")

        self.assertIn("SEGMENTED_ROW_STREAM", catalog)
        self.assertIn("CHUNKED_ROW_CONTINUATION", catalog)
        self.assertIn("fail-closed", report)
        self.assertIn("no app semantics", report)
        self.assertIn("3-AI consensus is reached", consensus)
        self.assertIn("status: internal_substrate", consensus)


if __name__ == "__main__":
    unittest.main()
