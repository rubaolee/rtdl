from __future__ import annotations

import unittest
from unittest.mock import patch

import rtdsl as rt
import rtdsl.partner_adapters as partner_adapters


class Goal2936MeasuredVectorPartnerSelectionHelperTest(unittest.TestCase):
    def test_helper_selects_fastest_measured_partner_without_claims(self) -> None:
        calls: list[str] = []

        def fake_grouped_vector_sum(
            vector_columns,
            *,
            group_count,
            partner,
            triton_offset_groups_per_program=1,
            return_metadata=False,
        ):
            calls.append(partner)
            payload = {
                "columns": {
                    "group_ids": list(range(group_count)),
                    "sum_x": [1.0, 2.0],
                    "sum_y": [3.0, 4.0],
                },
                "metadata": {
                    "partner": partner,
                    "adapter": "fake_grouped_vector_sum_2d_partner_columns",
                    "triton_offset_groups_per_program": triton_offset_groups_per_program,
                },
            }
            return payload if return_metadata else payload["columns"]

        perf_values = iter(
            (
                0.000,
                0.003,
                0.003,
                0.006,
                0.006,
                0.016,
                0.016,
                0.026,
                0.026,
                0.027,
                0.027,
                0.028,
            )
        )

        with patch.object(
            partner_adapters,
            "grouped_vector_sum_2d_partner_columns",
            side_effect=fake_grouped_vector_sum,
        ), patch.object(partner_adapters.time, "perf_counter", side_effect=lambda: next(perf_values)):
            result = rt.measured_grouped_vector_sum_2d_partner_selection(
                {
                    "torch": {"group_ids": [0, 1], "values_x": [1.0, 2.0], "values_y": [3.0, 4.0]},
                    "triton": {"group_ids": [0, 1], "values_x": [1.0, 2.0], "values_y": [3.0, 4.0]},
                    "cupy": {"group_ids": [0, 1], "values_x": [1.0, 2.0], "values_y": [3.0, 4.0]},
                },
                group_count=2,
                repeats=2,
                warmups=0,
            )

        metadata = result["metadata"]
        self.assertEqual(["torch", "torch", "triton", "triton", "cupy", "cupy"], calls)
        self.assertEqual("pass", metadata["status"])
        self.assertEqual("cupy", metadata["selected_partner"])
        self.assertEqual("cupy_wins_caller_requested_same_contract_measurement", metadata["selected_partner_reason"])
        self.assertFalse(metadata["silent_auto_selection_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["v2_5_release_authorized"])
        self.assertIn("caller_requested_same_contract_measurement", metadata["selection_policy"])

    def test_helper_skips_missing_partners_and_rejects_mismatched_outputs(self) -> None:
        def fake_grouped_vector_sum(
            vector_columns,
            *,
            group_count,
            partner,
            triton_offset_groups_per_program=1,
            return_metadata=False,
        ):
            sum_x = [1.0, 2.0] if partner == "torch" else [9.0, 9.0]
            payload = {
                "columns": {
                    "group_ids": list(range(group_count)),
                    "sum_x": sum_x,
                    "sum_y": [3.0, 4.0],
                },
                "metadata": {"partner": partner},
            }
            return payload if return_metadata else payload["columns"]

        perf_values = iter((0.0, 0.001, 0.001, 0.002))

        with patch.object(
            partner_adapters,
            "grouped_vector_sum_2d_partner_columns",
            side_effect=fake_grouped_vector_sum,
        ), patch.object(partner_adapters.time, "perf_counter", side_effect=lambda: next(perf_values)):
            result = rt.measured_grouped_vector_sum_2d_partner_selection(
                {
                    "torch": {"group_ids": [0, 1], "values_x": [1.0, 2.0], "values_y": [3.0, 4.0]},
                    "triton": {"group_ids": [0, 1], "values_x": [9.0, 9.0], "values_y": [3.0, 4.0]},
                },
                group_count=2,
                partners=("torch", "triton", "cupy"),
                repeats=1,
                warmups=0,
            )

        metadata = result["metadata"]
        candidates = {row["partner"]: row for row in metadata["candidate_results"]}
        self.assertEqual("torch", metadata["selected_partner"])
        self.assertEqual("mismatch", candidates["triton"]["status"])
        self.assertEqual("skipped", candidates["cupy"]["status"])
        self.assertEqual("no columns supplied for partner", candidates["cupy"]["reason"])

    def test_report_and_readiness_index_document_the_helper(self) -> None:
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        report = (
            root
            / "docs"
            / "reports"
            / "goal2936_measured_vector_partner_selection_helper_2026-06-01.md"
        )
        text = report.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=root)

        self.assertIn("measured_grouped_vector_sum_2d_partner_selection", text)
        self.assertIn("not a smart dispatcher", text)
        self.assertIn("automatic Triton/CuPy", text)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2936_measured_vector_partner_selection_helper_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2936_measured_vector_partner_selection_helper_green", packet["allowed_next_actions"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=root)["status"])


if __name__ == "__main__":
    unittest.main()
