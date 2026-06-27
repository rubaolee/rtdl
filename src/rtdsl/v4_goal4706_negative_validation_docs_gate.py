from __future__ import annotations

from dataclasses import dataclass

from .v4_goal4698_specialized_tier3_compile_cache import plan_v4_goal4698_specialized_tier3_compile


V4_GOAL4706_NEGATIVE_VALIDATION_DOCS_STATUS = (
    "goal4706_specialized_tier3_negative_validation_docs_gate_not_public_support"
)
V4_GOAL4706_NEXT_GOAL = "Goal4707 specialized Tier-3 external-review packet and debt consolidation"


@dataclass(frozen=True)
class V4Goal4706Gate:
    status: str
    accepted_example_status: str
    negative_rows: tuple[dict[str, object], ...]
    example_path: str
    next_goal: str
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "accepted_example_status": self.accepted_example_status,
            "negative_rows": self.negative_rows,
            "example_path": self.example_path,
            "next_goal": self.next_goal,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4706_negative_validation_docs_gate() -> V4Goal4706Gate:
    accepted = plan_v4_goal4698_specialized_tier3_compile(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol="custom_scalar_reduce_weighted_sum",
        callback_ptx=".common .global .align 8 .u64 _ZN08NumbaEnv33callbackB2v1B96;\n.visible .func custom_scalar_reduce_weighted_sum(){ret;}\n",
        toolchain_fingerprint="docs-example-toolchain",
    ).as_dict()
    cases = (
        (
            "arbitrary_python_callback",
            {
                "callback_shape": "custom_scalar_reduce",
                "callback_language": "python",
                "numba_cabi_device_function": False,
            },
        ),
        (
            "action_side_effect_callback",
            {
                "callback_shape": "custom_action",
                "callback_language": "numba",
                "numba_cabi_device_function": True,
                "mutates_shared_state": True,
                "action_semantics": True,
            },
        ),
        (
            "external_memory_mutation_callback",
            {
                "callback_shape": "custom_score",
                "callback_language": "numba",
                "numba_cabi_device_function": True,
                "writes_external_memory": True,
            },
        ),
        (
            "dynamic_sbt_direct_callable_hot_path",
            {
                "callback_shape": "custom_scalar_reduce",
                "callback_language": "numba",
                "numba_cabi_device_function": True,
                "sbt_direct_callable_hot_path": True,
                "raw_optix_callback": True,
            },
        ),
        (
            "non_scalar_variable_length_output",
            {
                "callback_shape": "custom_minmax",
                "callback_language": "numba",
                "numba_cabi_device_function": True,
                "returns_scalar": False,
                "variable_length_output": True,
            },
        ),
    )
    rows: list[dict[str, object]] = []
    for case_id, kwargs in cases:
        plan = plan_v4_goal4698_specialized_tier3_compile(**kwargs).as_dict()
        rows.append(
            {
                "case_id": case_id,
                "stage": plan["stage"],
                "error_code": plan["error_code"],
                "internal_compile_allowed": plan["internal_compile_allowed"],
                "tier3_public_support_authorized": plan["tier3_public_support_authorized"],
            }
        )
    return V4Goal4706Gate(
        status=V4_GOAL4706_NEGATIVE_VALIDATION_DOCS_STATUS,
        accepted_example_status=str(accepted["stage"]),
        negative_rows=tuple(rows),
        example_path="tools/_archive/future/v4/examples/simple_specialized_tier3_scalar_callback_candidate_example.py",
        next_goal=V4_GOAL4706_NEXT_GOAL,
    )


def validate_v4_goal4706_negative_validation_docs_gate() -> dict[str, object]:
    gate = v4_goal4706_negative_validation_docs_gate()
    payload = gate.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4706_NEGATIVE_VALIDATION_DOCS_STATUS:
        missing.append("status")
    if payload["accepted_example_status"] != "compile_cache_ready_not_executed":
        missing.append("accepted_example")
    if len(payload["negative_rows"]) < 5:
        missing.append("negative_rows")
    for row in payload["negative_rows"]:
        if row["stage"] != "rejected_before_compile":
            missing.append(f"{row['case_id']}_stage")
        if not str(row["error_code"] or "").startswith("RTDL_V4_TIER3_CALLBACK_REJECTED"):
            missing.append(f"{row['case_id']}_error_code")
        if row["internal_compile_allowed"] is not False:
            missing.append(f"{row['case_id']}_compile_allowed")
        if row["tier3_public_support_authorized"] is not False:
            missing.append(f"{row['case_id']}_support_authorized")
    for key in ("tier3_public_support_authorized", "release_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "gate": payload,
    }


__all__ = [
    "V4_GOAL4706_NEGATIVE_VALIDATION_DOCS_STATUS",
    "V4_GOAL4706_NEXT_GOAL",
    "V4Goal4706Gate",
    "v4_goal4706_negative_validation_docs_gate",
    "validate_v4_goal4706_negative_validation_docs_gate",
]
