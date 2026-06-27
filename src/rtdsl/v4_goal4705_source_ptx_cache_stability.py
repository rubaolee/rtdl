from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4705_SOURCE_PTX_CACHE_STABILITY_STATUS = (
    "goal4705_source_level_ptx_cache_stability_gate_not_public_support"
)
V4_GOAL4705_NEXT_GOAL = "Goal4706 specialized Tier-3 negative validation and user-doc example gate"


@dataclass(frozen=True)
class V4Goal4705CacheStabilitySummary:
    classification: str
    rows_checked: int
    stable_source_cache_keys: bool
    changed_ptx_changes_key: bool
    changed_toolchain_changes_key: bool
    next_goal: str
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "rows_checked": self.rows_checked,
            "stable_source_cache_keys": self.stable_source_cache_keys,
            "changed_ptx_changes_key": self.changed_ptx_changes_key,
            "changed_toolchain_changes_key": self.changed_toolchain_changes_key,
            "next_goal": self.next_goal,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def classify_v4_goal4705_source_ptx_cache_stability(rows: list[dict[str, object]]) -> dict[str, object]:
    stable_source = bool(rows) and all(bool(row.get("same_source_compile_cache_key_match")) for row in rows)
    changed_ptx = bool(rows) and all(bool(row.get("changed_ptx_changes_key")) for row in rows)
    changed_toolchain = bool(rows) and all(bool(row.get("changed_toolchain_changes_key")) for row in rows)
    passed = len(rows) >= 4 and stable_source and changed_ptx and changed_toolchain
    summary = V4Goal4705CacheStabilitySummary(
        classification=(
            "pass_source_level_cache_stability_gate_not_public_support"
            if passed
            else "fail_source_level_cache_stability_gate_repair_required"
        ),
        rows_checked=len(rows),
        stable_source_cache_keys=stable_source,
        changed_ptx_changes_key=changed_ptx,
        changed_toolchain_changes_key=changed_toolchain,
        next_goal=V4_GOAL4705_NEXT_GOAL if passed else "Repair source-level PTX cache stability before support docs",
    )
    return summary.as_dict()


def validate_v4_goal4705_source_ptx_cache_stability_contract() -> dict[str, object]:
    pass_rows = [
        {
            "same_source_compile_cache_key_match": True,
            "changed_ptx_changes_key": True,
            "changed_toolchain_changes_key": True,
        }
        for _ in range(4)
    ]
    fail_rows = pass_rows[:3] + [
        {
            "same_source_compile_cache_key_match": False,
            "changed_ptx_changes_key": True,
            "changed_toolchain_changes_key": True,
        }
    ]
    passed = classify_v4_goal4705_source_ptx_cache_stability(pass_rows)
    failed = classify_v4_goal4705_source_ptx_cache_stability(fail_rows)
    missing: list[str] = []
    if passed["classification"] != "pass_source_level_cache_stability_gate_not_public_support":
        missing.append("pass_classification")
    if failed["classification"] != "fail_source_level_cache_stability_gate_repair_required":
        missing.append("fail_classification")
    for key in ("tier3_public_support_authorized", "release_authorized", "performance_claim_authorized"):
        if passed[key] is not False or failed[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4705_SOURCE_PTX_CACHE_STABILITY_STATUS,
        "passing_example": passed,
        "failing_example": failed,
    }


__all__ = [
    "V4_GOAL4705_SOURCE_PTX_CACHE_STABILITY_STATUS",
    "V4_GOAL4705_NEXT_GOAL",
    "V4Goal4705CacheStabilitySummary",
    "classify_v4_goal4705_source_ptx_cache_stability",
    "validate_v4_goal4705_source_ptx_cache_stability_contract",
]
