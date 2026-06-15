from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md"
HANDOFF = ROOT / "docs/handoff/HANDOFF_3AI_GOAL4393_V3_0_M1_EXECUTION_GRAPH_IR_2026-06-15.md"
CLAUDE = ROOT / "docs/reviews/goal4393_claude_review_v3_0_m1_execution_graph_ir_2026-06-15.md"
GEMINI = ROOT / "docs/reviews/goal4393_gemini_review_v3_0_m1_execution_graph_ir_2026-06-15.md"
CONSENSUS = ROOT / "docs/reports/goal4393_3ai_consensus_v3_0_m1_execution_graph_ir_2026-06-15.md"
INIT = ROOT / "src/rtdsl/__init__.py"

V3_FORBIDDEN_PUBLIC_TOKENS = (
    "rayjoin",
    "lsi",
    "pip",
    "overlay",
    "dbscan",
    "rt_dbscan",
    "barnes",
    "barnes_hut",
    "raydb",
    "database",
    "sql",
    "robot",
    "robot_collision",
    "contact",
    "contact_manifold",
    "librts",
    "rtnn",
    "hausdorff",
    "triangle_counting",
    "paper",
    "author",
)


class Goal4393V30M1ExecutionGraphIRDesignTest(unittest.TestCase):
    def test_design_declares_m1_candidate_and_blocks_implementation(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        self.assertIn("rtdl.v3_0.execution_graph_ir.m1", text)
        self.assertIn("v3_0_m1_ir_frozen_m2_skeleton_allowed", text)
        self.assertIn("authorizes only M2 planner-skeleton work", text)
        self.assertIn("M2 may implement validators", text)
        self.assertIn("M2 may not implement", text)
        self.assertIn("native fused kernels", text)

    def test_public_api_candidate_names_are_app_agnostic(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        section = _section(text, "## Public API Candidate Names", "## Forbidden V3 Public API And Native Tokens")
        for name in (
            "GraphValue",
            "ValueKind",
            "Residency",
            "Lifetime",
            "StreamBinding",
            "PhaseMarker",
            "PrimitiveNode",
            "ContinuationNode",
            "PartnerNode",
            "MaterializeNode",
            "ValidationNode",
            "BackendPlan",
            "PreparedGraph",
            "ExecutionReport",
            "GraphValidationError",
        ):
            self.assertIn(name, section)
        lowered = section.lower()
        for token in V3_FORBIDDEN_PUBLIC_TOKENS:
            self.assertNotIn(token, lowered)

    def test_graph_value_stream_phase_and_evidence_contracts_are_first_class(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        for heading in (
            "## Graph Object",
            "## ClaimBoundary",
            "## PartnerPolicy",
            "## GraphValue",
            "## StreamBinding",
            "## PhaseMarker",
            "## PreparedGraph",
            "## Evidence Rule",
            "## Same-Contract Comparison Rule",
        ):
            self.assertIn(heading, text)
        for phrase in (
            "Device-resident values must have stream binding",
            "Host materialization must be represented by a `MaterializeNode`",
            "Same-stream wording requires `ordering=same_stream` plus CUDA event or Nsight evidence",
            "RT traversal, partner continuation, and materialization must be independently measurable",
            "same graph, same contract, same scale, phase split, repeated runs",
        ):
            self.assertIn(phrase, text)

    def test_claim_boundary_and_partner_policy_are_machine_checkable(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        for key in (
            "public_speedup_authorized",
            "rt_core_speedup_authorized",
            "true_zero_copy_authorized",
            "same_stream_claim_authorized",
            "device_resident_claim_authorized",
            "hidden_partner_selection_authorized",
            "automatic_partner_selection_authorized",
            "automatic_backend_selection_authorized",
            "app_specific_native_engine_authorized",
            "raw_optix_callback_user_api_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertIn(f"`{key}`", text)
        for key in (
            "explicit_partner_required",
            "best_partner",
            "numba_reference_required",
            "numba_omission_justification",
            "partner_timing_separated",
            "auto_selection_allowed",
            "allowed_partners",
            "benchmark_requires_dual_partner_rows",
        ):
            self.assertIn(f"`{key}`", text)
        self.assertIn("A missing key is a validation failure", text)
        self.assertIn("Benchmark graphs with PartnerNode must have `best_partner`", text)

    def test_node_types_preserve_partner_and_backend_boundaries(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        for heading in (
            "### PrimitiveNode",
            "### ContinuationNode",
            "### PartnerNode",
            "### MaterializeNode",
            "### ValidationNode",
        ):
            self.assertIn(heading, text)
        self.assertIn("users must not supply raw arbitrary OptiX callbacks as the public RTDL API", text)
        self.assertIn("Partner selection must be explicit. `auto` is invalid.", text)
        self.assertIn("best practical partner row and a Numba reference row are required", text)
        self.assertIn("Partner phase time must be separated from RT traversal time", text)
        for substructure in ("`BackendContract` required keys", "`LoweringHints` required keys", "`CapacityPolicy` required keys"):
            self.assertIn(substructure, text)
        for node_field in ("`backend_contract`", "`lowering_hints`", "`capacity_policy`", "`omission_justification`"):
            self.assertIn(node_field, text)
        self.assertIn("If `numba_reference_required=false` on a benchmark graph", text)

    def test_prepared_graph_schema_is_defined_without_execution_authority(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        section = _section(text, "## PreparedGraph", "## ExecutionReport")
        for field in (
            "graph_id",
            "ir_version",
            "validated_graph",
            "backend_plan",
            "state",
            "value_table",
            "phase_plan",
            "partner_policy",
            "claim_boundary",
            "validation_errors",
        ):
            self.assertIn(f"`{field}`", section)
        self.assertIn("no-execution prepared object", section)
        self.assertIn("must not execute native code", section)
        self.assertIn("all keys must remain false in M2", section)

    def test_legacy_schema_is_not_promoted_as_v3(self) -> None:
        text = DESIGN.read_text(encoding="utf-8")
        self.assertIn("Legacy single-kernel plan model", text)
        self.assertIn("Kept as compatibility", text)
        self.assertIn("must not be extended with new V3 app-specific workload enums", text)

    def test_handoff_requests_external_m1_freeze_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("Goal4393 V3.0 M1 Execution-Graph IR Review Handoff", text)
        self.assertIn("VERDICT: ACCEPT", text)
        self.assertIn("VERDICT: ACCEPT_WITH_NOTES", text)
        self.assertIn("VERDICT: REQUEST_CHANGES", text)
        self.assertIn("REQUEST_CHANGES blocks M2", text)
        self.assertIn("no-execution `PreparedGraph` skeleton", text)

    def test_future_v3_public_exports_do_not_use_app_specific_tokens(self) -> None:
        text = INIT.read_text(encoding="utf-8")
        v3_export_lines = [
            line
            for line in text.splitlines()
            if ".v3_" in line or "execution_graph" in line or "PreparedGraph" in line
        ]
        for line in v3_export_lines:
            lowered = line.lower()
            for token in V3_FORBIDDEN_PUBLIC_TOKENS:
                self.assertNotIn(token, lowered, f"forbidden V3 public token {token!r} in {line!r}")

    def test_future_v3_source_files_do_not_use_app_specific_public_names(self) -> None:
        future_files = [
            *ROOT.glob("src/rtdsl/v3_*.py"),
            *ROOT.glob("src/rtdsl/execution_graph*.py"),
            *ROOT.glob("src/native/**/*v3*.*"),
            *ROOT.glob("src/native/**/*execution_graph*.*"),
        ]
        identifier = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
        for path in future_files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            identifiers = {match.group(0).lower() for match in identifier.finditer(text)}
            for token in V3_FORBIDDEN_PUBLIC_TOKENS:
                self.assertNotIn(token, identifiers, f"forbidden V3 identifier {token!r} in {path}")

    def test_consensus_records_acceptable_reviews_when_present(self) -> None:
        if not CONSENSUS.exists():
            self.skipTest("consensus file is created after external review")
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("v3_0_m1_ir_frozen_m2_skeleton_allowed", text)
        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        self.assertIn("M2 planner-skeleton implementation", text)
        self.assertIn("RC-1", text)
        self.assertIn("RC-2", text)
        self.assertIn("RC-3", text)
        self.assertIn("RC-4", text)
        self.assertNotIn("VERDICT: REQUEST_CHANGES", text)

        for review_path in (CLAUDE, GEMINI):
            review = review_path.read_text(encoding="utf-8")
            match = re.search(r"^VERDICT: (ACCEPT|ACCEPT_WITH_NOTES|REQUEST_CHANGES)$", review, re.MULTILINE)
            self.assertIsNotNone(match, f"{review_path} must include an exact verdict line")
            self.assertNotEqual("REQUEST_CHANGES", match.group(1))


def _section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


if __name__ == "__main__":
    unittest.main()
