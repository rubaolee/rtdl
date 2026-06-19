from __future__ import annotations

from pathlib import Path
import unittest

from scripts import run_test_matrix


ROOT = Path(__file__).resolve().parents[1]
REFRAMING_NOTE = (
    ROOT
    / "docs"
    / "reviews"
    / "v4_reframing_note_rt_core_operator_for_python_gpu_ecosystem_2026-06-19.md"
)
CODEX_RESPONSE = (
    ROOT / "docs" / "reviews" / "codex_v4_reframing_ingestion_response_2026-06-19.md"
)
ROUTE_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_m1_route_consensus_2026-06-19.md"
)
DESIGN = ROOT / "docs" / "engineering" / "rtdl_v4_0_design_review_packet_2026-06-19.md"
ACTIVE_ABI_NOTE = ROOT / "docs" / "engineering" / "rtdl_v4_0_active_abi_slice_2026-06-19.md"
ACTIVE_README = ROOT / "src" / "v4" / "README.md"
V4_OPERATOR = ROOT / "src" / "rtdsl" / "v4_0_device_array_operator.py"


def _compact(text: str) -> str:
    return " ".join(text.split())


class V40ReframedProductDesignTest(unittest.TestCase):
    def test_reframing_note_carries_missing_rt_core_lane_pitch(self) -> None:
        note = REFRAMING_NOTE.read_text(encoding="utf-8")

        for token in (
            "The pitch: the missing RT-core lane",
            "CUDA cores",
            "Tensor cores",
            "RT cores",
            "RTDL is the missing RT-core lane for the Python GPU ecosystem",
            "Python actors only",
            "full public multi-language C ABI and SDK packaging are V4.x",
            "Phase 1",
            "Python device-array RT-core operator",
        ):
            self.assertIn(token, note)

    def test_design_packet_leads_with_python_gpu_product_not_c_abi_product(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        compact = _compact(design)

        for token in (
            "Product Pitch: The Missing RT-Core Lane",
            "positions RTDL as the missing RT-core lane for the Python GPU ecosystem",
            "V4.0 is Python actors only",
            "CuPy, Numba, Triton, PyTorch",
            "There is no C++ host in current V4.0 scope",
            "The C ABI remains real, but it is the basement under that Python product",
            "Phase 1: Python Device-Array RT-Core Operator",
            "Phase 2: C ABI Substrate Hardening",
            "Phase 3: Non-Python Hosts And SDK Packaging",
            "Under the current Python-only V4.0 scope decision, this phase is V4.x",
            "M2: Python Device-Array Intake",
            "M3: First Python RT-Core Operator Route",
            "fixed_radius_count_threshold_2d",
            "fixed-size `query_ids`, `neighbor_counts`, and `threshold_flags`",
            "M4: Zero-Copy Evidence Packet",
            "M5: C ABI Substrate Hardening",
            "Non-Python Host V4.x Path",
        ):
            self.assertIn(token, compact)

        for stale in (
            "Phase 1: CPU Host Route",
            "Phase 4: CUDA Device-Buffer Route",
            "M2: C ABI 0.2 Control Plane",
            "M3: First Real Query Route",
            "Scope decision made: non-Python hosts are either V4.0 goals or V4.x goals",
            "Are non-Python hosts (C++/Rust/PyTorch-C++) V4.0 goals",
        ):
            self.assertNotIn(stale, compact)

    def test_scope_decision_moves_public_non_python_sdk_to_v4_x(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (DESIGN, ACTIVE_ABI_NOTE, CODEX_RESPONSE)
        )

        for token in (
            "V4.0 is Python actors only",
            "non-Python hosts are V4.x",
            "public multi-language C ABI",
            "generated C/C++/Rust",
            "pkg-config/CMake",
        ):
            self.assertIn(token, combined)

        self.assertIn(
            "full public multi-language C ABI packaging is V4.x",
            CODEX_RESPONSE.read_text(encoding="utf-8"),
        )

    def test_m1_route_consensus_freezes_fixed_radius_count_threshold(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (DESIGN, ROUTE_CONSENSUS, ACTIVE_ABI_NOTE, ACTIVE_README, V4_OPERATOR)
        )
        compact = _compact(combined)

        for token in (
            "fixed_radius_count_threshold_2d",
            "not variable-length neighbor rows",
            "caller-owned CUDA point columns",
            "query_ids",
            "neighbor_counts",
            "threshold_flags",
            "synchronize that stream before return",
            "caller_stream_supported_synchronous",
            "Ray/triangle any-hit is not rejected",
            "V4_0_M1_ROUTE_ID",
            "run_v4_fixed_radius_count_threshold_2d",
        ):
            self.assertIn(token, compact)

        self.assertNotIn("First product route: Fixed-radius neighbors, ray/triangle any-hit", compact)

    def test_active_v4_abi_slice_is_substrate_not_product_headline(self) -> None:
        active_note = ACTIVE_ABI_NOTE.read_text(encoding="utf-8")
        readme = ACTIVE_README.read_text(encoding="utf-8")

        for text in (active_note, readme):
            compact = _compact(text)
            self.assertIn("Phase 2 substrate", compact)
            self.assertIn("not the Phase 1 V4.0 product proof", compact)

        self.assertIn("not the V4.0 product headline", active_note)
        self.assertIn("not the V4.0 headline", _compact(readme))

    def test_v4_active_matrix_includes_design_reframing_gate(self) -> None:
        modules = run_test_matrix.group_modules("v4_active")
        self.assertIn("tests.v4_0_active_abi_control_plane_test", modules)
        self.assertIn("tests.v4_0_reframed_product_design_test", modules)
        self.assertIn("tests.v4_0_m1_fixed_radius_route_test", modules)


if __name__ == "__main__":
    unittest.main()
