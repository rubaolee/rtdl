from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


FULL_APP_SPEEDUP_MIN_V4_V2 = 1.20
FULL_APP_SPEEDUP_MIN_V4_V3 = 1.05
NO_REGRESSION_FLOOR = 0.98
HAUSDORFF_PRIMARY_WALL_SPEEDUP_MIN_V4_V2 = 1.20
HAUSDORFF_HOT_SPEEDUP_MIN_V4_V3 = 1.20
HAUSDORFF_PREPARE_NO_REGRESSION_FLOOR = 0.80


@dataclass(frozen=True)
class V4AppBenchmarkRow:
    app: str
    v4_vs_v2_14_hot_speedup: float | None
    v4_vs_v3_0_2_hot_speedup: float | None
    v3_0_2_vs_v2_14_hot_speedup: float | None
    all_returncode_zero: bool
    all_correctness_parity_or_skipped_oracle: bool
    claim_class: str
    pass_frozen_speed_bar: bool
    contributes_to_formal_high_performance: bool
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "v4_vs_v2_14_hot_speedup": self.v4_vs_v2_14_hot_speedup,
            "v4_vs_v3_0_2_hot_speedup": self.v4_vs_v3_0_2_hot_speedup,
            "v3_0_2_vs_v2_14_hot_speedup": self.v3_0_2_vs_v2_14_hot_speedup,
            "all_returncode_zero": self.all_returncode_zero,
            "all_correctness_parity_or_skipped_oracle": self.all_correctness_parity_or_skipped_oracle,
            "claim_class": self.claim_class,
            "pass_frozen_speed_bar": self.pass_frozen_speed_bar,
            "contributes_to_formal_high_performance": self.contributes_to_formal_high_performance,
            "explanation": self.explanation,
        }


def load_goal4654_summary(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def analyze_goal4654_summary(summary: dict[str, Any]) -> dict[str, Any]:
    native_provenance_blocker = not bool(
        summary.get("analysis", {}).get("formal_tag_native_optix_purity")
    )
    app_rows = [
        _classify_app_row(row, native_provenance_blocker=native_provenance_blocker)
        for row in summary.get("analysis", {}).get("app_scorecard", [])
    ]
    true_v4_candidates = [
        row for row in app_rows if row.claim_class == "true_v4_operator_win_candidate"
    ]
    contributing = [row for row in app_rows if row.contributes_to_formal_high_performance]
    failed_or_parity = [
        row
        for row in app_rows
        if row.claim_class
        in {
            "parity_not_v4_speed_win",
            "modest_runtime_gain_below_formal_bar",
            "regression",
            "blocked_missing_metric_or_correctness",
        }
    ]
    blocking_reasons: list[str] = []
    if native_provenance_blocker:
        blocking_reasons.append("old_version_optix_uses_v4_compatibility_native_library")
    if failed_or_parity:
        blocking_reasons.append("most_full_app_rows_do_not_pass_frozen_speed_bar")
    if len(true_v4_candidates) < 2:
        blocking_reasons.append("insufficient_independent_true_v4_app_wins")

    formal_supported = not blocking_reasons and len(contributing) >= 2
    decision_label = (
        "formal_high_performance_v4_supported"
        if formal_supported
        else "bounded_operator_v4_only__app_level_high_performance_not_supported"
    )
    return {
        "schema": "rtdl.v4.goal4655.app_benchmark_analysis.v1",
        "source_schema": summary.get("schema"),
        "source_status": summary.get("status"),
        "decision_label": decision_label,
        "formal_high_performance_v4_supported": formal_supported,
        "bounded_operator_v4_only": not formal_supported,
        "partner_migration_lock_preserved": True,
        "native_provenance_blocker": native_provenance_blocker,
        "blocking_reasons": blocking_reasons,
        "true_v4_candidate_app_count": len(true_v4_candidates),
        "contributing_app_count": len(contributing),
        "app_rows": [row.to_dict() for row in app_rows],
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_high_performance_claim_authorized": False,
            "partner_migration_counts_as_v4_speed_win": False,
            "native_provenance_blocker_must_remain_visible": native_provenance_blocker,
        },
    }


def _classify_app_row(row: dict[str, Any], *, native_provenance_blocker: bool) -> V4AppBenchmarkRow:
    app = str(row.get("app"))
    v4_v2 = _float_or_none(row.get("v4_vs_v2_14_hot_speedup"))
    v4_v3 = _float_or_none(row.get("v4_vs_v3_0_2_hot_speedup"))
    v3_v2 = _float_or_none(row.get("v3_0_2_vs_v2_14_hot_speedup"))
    ok = bool(row.get("all_returncode_zero")) and bool(
        row.get("all_correctness_parity_or_skipped_oracle")
    )
    pass_bar = (
        ok
        and v4_v2 is not None
        and v4_v3 is not None
        and v4_v2 >= FULL_APP_SPEEDUP_MIN_V4_V2
        and v4_v3 >= FULL_APP_SPEEDUP_MIN_V4_V3
    )
    no_regression = (
        v4_v2 is not None
        and v4_v3 is not None
        and v4_v2 >= NO_REGRESSION_FLOOR
        and v4_v3 >= NO_REGRESSION_FLOOR
    )

    if app == "hausdorff_xhd":
        return _classify_hausdorff_row(
            row,
            native_provenance_blocker=native_provenance_blocker,
            ok=ok,
            v4_v2_hot=v4_v2,
            v4_v3_hot=v4_v3,
            v3_v2_hot=v3_v2,
        )

    if not ok or v4_v2 is None or v4_v3 is None:
        claim_class = "blocked_missing_metric_or_correctness"
        explanation = "Missing metric, nonzero return code, or missing correctness evidence."
    elif not no_regression:
        claim_class = "regression"
        explanation = "At least one V4 app-level ratio falls below the 0.98 no-regression floor."
    elif pass_bar and v3_v2 is not None and v3_v2 >= FULL_APP_SPEEDUP_MIN_V4_V2:
        claim_class = "historical_route_evolution_plus_modest_v4_increment"
        explanation = (
            "The V4/V2.14 row passes numerically, but most of the V2.14 delta "
            "already exists in V3.0.2; this cannot be framed as a clean new V4 win."
        )
    elif pass_bar:
        claim_class = "true_v4_operator_win_candidate"
        explanation = "The row passes the frozen V4/V2.14 and V4/V3.0.2 speed bars."
    elif v4_v2 >= FULL_APP_SPEEDUP_MIN_V4_V3 or v4_v3 >= FULL_APP_SPEEDUP_MIN_V4_V3:
        claim_class = "modest_runtime_gain_below_formal_bar"
        explanation = "The row is at parity or modestly faster, but below the frozen formal speed bar."
    else:
        claim_class = "parity_not_v4_speed_win"
        explanation = "The row is effectively parity and does not prove a V4 speed win."

    contributes = (
        claim_class == "true_v4_operator_win_candidate"
        and not native_provenance_blocker
    )
    return V4AppBenchmarkRow(
        app=app,
        v4_vs_v2_14_hot_speedup=v4_v2,
        v4_vs_v3_0_2_hot_speedup=v4_v3,
        v3_0_2_vs_v2_14_hot_speedup=v3_v2,
        all_returncode_zero=bool(row.get("all_returncode_zero")),
        all_correctness_parity_or_skipped_oracle=bool(
            row.get("all_correctness_parity_or_skipped_oracle")
        ),
        claim_class=claim_class,
        pass_frozen_speed_bar=pass_bar,
        contributes_to_formal_high_performance=contributes,
        explanation=explanation,
    )


def _classify_hausdorff_row(
    row: dict[str, Any],
    *,
    native_provenance_blocker: bool,
    ok: bool,
    v4_v2_hot: float | None,
    v4_v3_hot: float | None,
    v3_v2_hot: float | None,
) -> V4AppBenchmarkRow:
    v4_v2_primary = _float_or_none(row.get("v4_vs_v2_14_primary_wall_speedup"))
    prepare_v4_v3 = _float_or_none(row.get("v4_prepare_vs_v3_0_2_speedup"))
    probe_ok = bool(row.get("coordinate_normalized_1m_correctness_probe_passed"))
    pass_bar = (
        ok
        and probe_ok
        and v4_v2_primary is not None
        and v4_v3_hot is not None
        and prepare_v4_v3 is not None
        and v4_v2_primary >= HAUSDORFF_PRIMARY_WALL_SPEEDUP_MIN_V4_V2
        and v4_v3_hot >= HAUSDORFF_HOT_SPEEDUP_MIN_V4_V3
        and prepare_v4_v3 >= HAUSDORFF_PREPARE_NO_REGRESSION_FLOOR
    )

    if not ok:
        claim_class = "blocked_missing_metric_or_correctness"
        explanation = "Hausdorff row failed return-code or directed-distance correctness parity."
    elif not probe_ok:
        claim_class = "blocked_missing_metric_or_correctness"
        explanation = "Hausdorff requires the coordinate-normalized 1M correctness-boundary probe."
    elif v4_v2_primary is None or v4_v3_hot is None or prepare_v4_v3 is None:
        claim_class = "blocked_missing_metric_or_correctness"
        explanation = "Hausdorff is missing primary wall, V3 hot, or prepare-window denominator."
    elif pass_bar:
        claim_class = "true_v4_operator_win_candidate"
        explanation = (
            "Hausdorff passes its frozen custom bar: V4/V2.14 primary wall >= 1.20x, "
            "V4/V3 hot >= 1.20x, prepare >= 0.80x, and 1M correctness-boundary probe passes."
        )
    elif v4_v2_primary < NO_REGRESSION_FLOOR or v4_v3_hot < NO_REGRESSION_FLOOR or prepare_v4_v3 < HAUSDORFF_PREPARE_NO_REGRESSION_FLOOR:
        claim_class = "regression"
        explanation = "Hausdorff fails at least one no-regression floor in the frozen custom bar."
    else:
        claim_class = "modest_runtime_gain_below_formal_bar"
        explanation = "Hausdorff is valid but below at least one frozen custom speed bar."

    contributes = claim_class == "true_v4_operator_win_candidate" and not native_provenance_blocker
    return V4AppBenchmarkRow(
        app="hausdorff_xhd",
        v4_vs_v2_14_hot_speedup=v4_v2_hot,
        v4_vs_v3_0_2_hot_speedup=v4_v3_hot,
        v3_0_2_vs_v2_14_hot_speedup=v3_v2_hot,
        all_returncode_zero=bool(row.get("all_returncode_zero")),
        all_correctness_parity_or_skipped_oracle=bool(
            row.get("all_correctness_parity_or_skipped_oracle")
        ),
        claim_class=claim_class,
        pass_frozen_speed_bar=pass_bar,
        contributes_to_formal_high_performance=contributes,
        explanation=explanation,
    )


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None
