#!/usr/bin/env python3
"""Build the Goal5787 CGO claim matrix and programming-responsibility ledger.

This script is intentionally read-only with respect to every predecessor.  It
rehashes the frozen authorities, derives all performance classifications from
the Goal5785 evaluation, and emits only new Goal5787 integration artifacts.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"

PINS = {
    "history/internal_docs/review_goal5785_v6_rtx4000ada_final_result_20260816.md": "d34673a81a029871f66999506bf88950626a2c1530bbff20fca72a2bd4884802",
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz": "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a",
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EVALUATION.json": "af630fa74ff6b60d1917234b7998e703d8ee60cf91c47cf4ef49ccebf065846a",
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz": "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41",
    "history/internal_docs/goal5786_goal5785_causal_stratification_result_20260816.json": "6b5701c31cf17aac105484d224228ef704a4508844e151c2c89d495f505de7b9",
    "history/internal_docs/goal5786_independent_causal_recount_20260816.json": "cf9fb5ff39cdd9f0ff132193ac592337161c156281abcaf47c1497fa66097952",
    "history/internal_docs/goal5786_exact_source_mechanism_audit_20260816.json": "7bb0fb290d47c9796b75e1822296d4b310f923a1a5e220e2c1c3c7270c489455",
    "history/internal_docs/call_for_review_goal5786_goal5785_clear_loss_causal_stratification_20260816.md": "1bdb34c689e88f59c469f42f2dfa6592c3a57a7a8ca0cd16898fb252d4d01948",
    "history/internal_docs/goal5783_postfreeze_held_out_rtxrmq_result_20260814.json": "eaf65a55367722d67933b7531bd614bfd213e375c331eb79d2604d4b0a1cd882",
    "history/internal_docs/goal5783_postfreeze_held_out_rtxrmq_evidence_20260814.tar.gz": "3bbc85e15aa89afba0c9b1332642e1ed12e7dab354debd91462761557522cf36",
    "history/internal_docs/review_goal5783_postfreeze_held_out_rtxrmq_20260814.md": "2dd0864e9db0708f13d48d0c2295419c2bdfe7f80cd93792a85745d0293f006b",
    "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz": "50e37b1d4a311bdde40d30392cd9201bc781e5d228d72df4f430b3e12f81955c",
    "history/internal_docs/goal5767_v4_usable_rc_v6_twin_20260812.tar.gz": "50e37b1d4a311bdde40d30392cd9201bc781e5d228d72df4f430b3e12f81955c",
    "history/internal_docs/goal5767_v4_usable_release_surface_result_20260812.json": "15a6aa7bc95d88296ab99020ccc7c50880b8ba8a15ef61c395c124418992645d",
    "history/internal_docs/goal5767_release_audit_20260812.json": "8cd757d445edff88e471e08c03cebdb3688c495b0842b1028c8b4dda23371989",
    "history/internal_docs/goal5767_v4_usable_release_surface_evidence_20260812.tar.gz": "695366007a2b64fe2ebd546a2e1818253adfbd3944f56e963efc912f53171e30",
    "history/internal_docs/external_reviewer_critical_assessment_of_v3_for_cgo_positioning.md": "6a9e9980f999da4a16c985b5258f0febdb27eeb75a54b03ab82f29b8ae2b6b3d",
    "history/internal_docs/v4_cgo_next_stage_goal_register_after_goal5776_20260814.json": "a3d9cf939deccea5af07a930e2e05abfe90b9dec281e9a90a48225f375230c29",
}


APP_RESPONSIBILITIES = {
    "particle_tracking": {
        "paper_algorithm": "tetrahedral closest-face cell transition",
        "v4_composition": ["built-in triangle GAS", "restricted closest-hit state update", "prepared lifecycle"],
        "application_owned": ["tetrahedral domain encoding", "transition semantics", "input/output contract"],
        "system_owned": ["restricted callback validation", "Callback IR/PTX lowering", "OptiX program/SBT binding", "fault/status receipt"],
        "legacy_partner_caveat": "The built-in triangle traversal is an RTDL physical partner; V4 does not synthesize OptiX itself.",
    },
    "triangle_counting": {
        "paper_algorithm": "RT-1A2 and RT-2A1 (both application-selected)",
        "v4_composition": ["built-in triangle traversal", "restricted per-hit reduction callback", "segmented device reduction"],
        "application_owned": ["choice of RT-1A2 versus RT-2A1", "graph orientation/layout", "triangle-count output contract"],
        "system_owned": ["callback safety proof", "PTX/wrapper generation", "capacity/status handling", "prepared execution lifecycle"],
        "legacy_partner_caveat": "DEFAULT never chooses between the two paper algorithms.",
    },
    "raydb": {
        "paper_algorithm": "partitioned triangle grouped-I64 sum",
        "v4_composition": ["bounded relation emission", "partitioned triangle traversal", "grouped exact-I64 reduction"],
        "application_owned": ["query relation and grouping keys", "partition layout", "exact aggregate contract"],
        "system_owned": ["bounded emission ABI", "overflow fail-close", "OptiX binding", "grouped reduction composition"],
        "legacy_partner_caveat": "The physical traversal family is a trusted partner, not arbitrary user PTX.",
    },
    "librts": {
        "paper_algorithm": "AABB point/range containment counts",
        "v4_composition": ["bounded relation emission", "AABB traversal", "count reduction"],
        "application_owned": ["spatial predicates", "column/schema bindings", "count output contract"],
        "system_owned": ["typed physical schema", "AABB/GAS ABI", "capacity proof", "behavioral traversal receipt"],
        "legacy_partner_caveat": "V4 supplies a safe composition surface; it does not expose arbitrary intersection callbacks.",
    },
    "x_hd": {
        "paper_algorithm": "directed exact max-of-nearest witness",
        "v4_composition": ["exact-predicate/global-witness callback", "cell-MBR traversal", "deterministic witness reduction"],
        "application_owned": ["directed Hausdorff semantics", "source/target schema", "exact witness output"],
        "system_owned": ["exact-state validation", "witness tie-breaking", "OptiX wrapper", "fail-closed continuation composition"],
        "legacy_partner_caveat": "The canonical paper route is fixed; V4 makes no cost-based choice among application algorithms.",
    },
    "rtnn": {
        "paper_algorithm": "exact ranked distance-window top-k",
        "v4_composition": ["multiround spatial callback", "ranked bounded-selection state", "deterministic top-k"],
        "application_owned": ["distance/search contract", "K and domain bounds", "ordered result contract"],
        "system_owned": ["round/refit lifecycle", "state/capacity validation", "PTX generation", "launch receipt"],
        "legacy_partner_caveat": "Metric-specific traversal remains a trusted physical family.",
    },
    "rt_dbscan": {
        "paper_algorithm": "bounded-radius graph component partition",
        "v4_composition": ["multiround radius-graph emission", "grouped continuation", "component partition"],
        "application_owned": ["radius/min-points semantics", "dataset bounds", "partition output contract"],
        "system_owned": ["bounded edge emission", "overflow/status contract", "prepared refinement proof", "OptiX composition"],
        "legacy_partner_caveat": "V4 combines callback-generated work with trusted grouped/partition partners; it does not claim all stages run on RT cores.",
    },
    "rayjoin": {
        "paper_algorithm": "six-batch planar overlay",
        "v4_composition": ["planar-map OptiX producer", "typed columnar carrier", "grouped exact reduction"],
        "application_owned": ["six-batch paper schedule", "overlay predicates", "six exact output tables"],
        "system_owned": ["typed carrier/effect checks", "capacity and signed-I64 proof", "producer/reducer lifecycle", "physical receipts"],
        "legacy_partner_caveat": "This path substantially reuses reviewed legacy physical partners; V4 does not claim callback-generated replacement of every native stage.",
    },
    "rt_barneshut": {
        "paper_algorithm": "aggregate-hierarchy inverse-square scalar force",
        "v4_composition": ["hierarchy-frontier callback", "aggregate state", "deterministic force reduction"],
        "application_owned": ["Barnes-Hut acceptance semantics", "body/tree schema", "force output contract"],
        "system_owned": ["hierarchy/GAS ABI", "frontier safety validation", "callback lowering", "prepared traversal lifecycle"],
        "legacy_partner_caveat": "Tree construction and aggregate-hierarchy traversal are explicit trusted partners.",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def classify(ci: list[float]) -> str:
    lo, hi = ci
    if lo > 1.0:
        return "ci_clear_v4_win"
    if hi < 1.0:
        return "ci_clear_v4_loss"
    return "uncertain_ci_crosses_one"


def verify_pins() -> list[dict[str, object]]:
    rows = []
    for relative, expected in PINS.items():
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"missing frozen authority: {relative}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"frozen authority drift: {relative}: {actual} != {expected}")
        rows.append({"path": relative, "sha256": actual, "verified": True})
    return rows


def build_claim_matrix(pins: list[dict[str, object]]) -> dict:
    evaluation = load_json(
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EVALUATION.json"
    )
    rows = []
    by_lifecycle: dict[str, Counter] = defaultdict(Counter)
    by_app: dict[str, Counter] = defaultdict(Counter)
    for source in evaluation["rows"]:
        ci_class = classify(source["bootstrap_ci95"])
        lifecycle = source["lifecycle"]
        app = source["app"]
        by_lifecycle[lifecycle][ci_class] += 1
        by_app[app][ci_class] += 1
        rows.append({
            "row_id": source["row_id"],
            "app": app,
            "paper_algorithm": source["paper_algorithm"],
            "lifecycle": lifecycle,
            "pair_count": source["pair_count"],
            "ratio": "v2_direct_over_v4",
            "paired_ratio_median": source["paired_ratio_median"],
            "bootstrap_ci95": source["bootstrap_ci95"],
            "ci_classification": ci_class,
            "median_no_slower_pass": source["paired_ratio_median"] >= 1.0,
            "evidence_authority": "Goal5785 EVALUATION + immutable raw archive",
            "forbidden_reading": "No row may be aggregated across applications or lifecycles; a CI-crossing row is not a clear win or clear loss.",
        })
    counts = Counter(row["ci_classification"] for row in rows)
    medians = Counter("median_pass" if row["median_no_slower_pass"] else "median_fail" for row in rows)
    if counts != Counter({"ci_clear_v4_win": 11, "ci_clear_v4_loss": 10, "uncertain_ci_crosses_one": 13}):
        raise RuntimeError(f"unexpected Goal5785 CI split: {counts}")
    if medians != Counter({"median_pass": 16, "median_fail": 18}):
        raise RuntimeError(f"unexpected Goal5785 median split: {medians}")
    if evaluation["worker_count"] != 464 or evaluation["independent_row_count"] != 34:
        raise RuntimeError("Goal5785 shape drift")

    mechanism_families = [
        {
            "name": "triangle_callback_plus_device_reduction_fusion",
            "support": "10 CI-clear wins: four cold and six prepared Triangle rows",
            "scope": "three frozen graph datasets and the two application-selected paper algorithms",
            "forbidden_reading": "Not a universal callback-fusion result and not evidence that DEFAULT selected between RT-1A2 and RT-2A1.",
        },
        {
            "name": "particle_prepared_fused_callback_execution",
            "support": "one prepared CI-clear win; median V2/V4 7.9109607549, CI [7.4345859824, 8.3070279950]",
            "scope": "prepared-first-execute on the frozen particle unit",
            "forbidden_reading": "The same unit is a cold CI-clear loss (median 0.4735120313); preparation is not free.",
        },
    ]

    return {
        "schema": "rtdl.goal5787.cgo_claim_matrix.v1",
        "goal": 5787,
        "frozen_authorities": pins,
        "primary_paper_spine": "V2-direct baseline plus V4 restricted-Python callback system",
        "performance": {
            "hardware": "RTX 4000 Ada / CC8.9 ordinary POD",
            "worker_count": 464,
            "independent_row_count": 34,
            "median_split": dict(medians),
            "ci_split": dict(counts),
            "cold": dict(by_lifecycle["installed_cold_compile_prepare_execute"]),
            "prepared": dict(by_lifecycle["prepared_first_execute"]),
            "by_app": {app: dict(counts_) for app, counts_ in sorted(by_app.items())},
            "rows": rows,
            "all_row_no_slower_claimed": False,
            "universal_outperformance_claimed": False,
        },
        "mechanism_families": mechanism_families,
        "correctness_and_physical_lineage": {
            "claim": "All 464 Goal5785 endpoints matched their frozen output contracts and carried behaviorally true-OptiX receipts.",
            "scope": "exact Goal5785 source/native/plan, nine applications, 34 rows, RTX 4000 Ada cohort",
            "forbidden_reading": "This is not RT-core silicon-utilization measurement, author parity, or universal application coverage.",
        },
        "held_out_exam": {
            "claim": "One externally published post-freeze RTXRMQ instance was expressed without changing the frozen V4 core and passed four local/Home functional lanes.",
            "scope": "small functional existence proof using the existing restricted callback family",
            "forbidden_reading": "No performance, full Algorithm-5 reproduction, Paper-App status, random-sample generalization rate, or universal coverage claim.",
        },
        "portable_artifact": {
            "claim": "Goal5767 v6 is a byte-twinned, private-cache-free V4 4.0.0rc1 portable research artifact with clean validation evidence.",
            "scope": "functional/usability RC at its exact Goal5767 source identity",
            "forbidden_reading": "The Goal5767 RC source is not the Goal5785 performance source and cannot by itself reproduce Goal5785 numbers.",
        },
        "causal_status": {
            "claim": "Goal5786 locates the ten Goal5785 CI-clear losses into eight cold preparation-envelope, one cold execute-envelope, and one prepared execute-envelope rows.",
            "leaf_cache_census": {"hits": 928, "misses": 0, "disabled": 0},
            "forbidden_reading": "Location is not eliminability and observed seconds are not predicted savings; RayJoin/X-HD finer causes remain unknown.",
            "external_review_status": "owner-controlled CFR exists; no owner-returned external verdict is claimed here",
        },
        "v3_disposition": {
            "permitted_claim": "verified fail-closed deterministic one-to-one lowering over a curated partial provider catalog",
            "paper_role": "predecessor/ablation or bounded appendix only",
            "forbidden_claims": [
                "automatic coverage of unseen applications",
                "cost-based physical-plan optimizer",
                "total lowering for every legal high-level request",
                "automatic discovery of new RT algorithms",
                "central implementation or performance path of the V2+V4 paper",
            ],
        },
        "global_forbidden_claims": [
            "V4 is faster than V2 on every row",
            "V4 is universally competitive on arbitrary applications or GPUs",
            "V4 matches or beats author implementations",
            "the receipts measure hardware RT-core utilization",
            "prepared work is free or replaces cold results",
            "Goal5783 proves a generalization rate",
            "Goal5767 exact source reproduces Goal5785 performance",
            "CGO submission is complete or accepted",
        ],
        "claim_boundary": {
            "manuscript_draft_authorized": True,
            "artifact_candidate_freeze_authorized": True,
            "new_performance_claimed": False,
            "new_pod_used_or_authorized": False,
            "submission_ready_claimed": False,
            "public_release_claimed": False,
        },
    }


def build_programming_ledger() -> dict:
    if set(APP_RESPONSIBILITIES) != {
        "particle_tracking", "triangle_counting", "raydb", "librts", "x_hd",
        "rtnn", "rt_dbscan", "rayjoin", "rt_barneshut",
    }:
        raise RuntimeError("nine-application responsibility ledger is incomplete")
    rows = []
    for app, body in APP_RESPONSIBILITIES.items():
        rows.append({"app": app, **body})
    return {
        "schema": "rtdl.goal5787.programming_responsibility_ledger.v1",
        "goal": 5787,
        "methodology": {
            "unit": "semantic and engineering responsibility, not raw lines of code",
            "developer_time_measured": False,
            "productivity_multiplier_claimed": False,
            "raw_loc_ratio_used_as_primary_metric": False,
            "shared_v4_infrastructure_counted_once": True,
            "evaluation_harness_excluded_from_application_burden": True,
            "legacy_partner_reuse_disclosed_per_application": True,
        },
        "v4_shared_system_responsibilities_counted_once": [
            "restricted-Python AST validation and typed Callback IR",
            "CPU reference interpreter and differential semantic oracle",
            "trusted IR-to-Python/Numba PTX generation",
            "OptiX module/program-group/pipeline/SBT wrapper composition",
            "typed physical schema and GAS ABI",
            "explicit device fault/status envelope and fail-closed validation",
            "prepared lifecycle, resource ownership, and cache identity",
            "behavioral traversal receipts and source/native/plan binding",
        ],
        "manual_optix_obligations_removed_from_application_programmer": [
            "hand-written PTX/CUDA callback ABI plumbing",
            "manual OptiX module, program-group, pipeline and SBT assembly",
            "manual payload/register layout coordination",
            "manual launch-status buffer and error-envelope plumbing",
            "manual program/traversable provenance receipt integration",
            "manual cache/native/source identity binding",
        ],
        "responsibilities_not_removed": [
            "choosing the paper/application algorithm",
            "defining application semantics and exact output contracts",
            "selecting an available V4 composition family",
            "providing data layout, capacity and domain bounds",
            "adding a new trusted physical family when existing V4 roles cannot express the algorithm",
            "validating application-level correctness against an independent oracle",
        ],
        "applications": rows,
        "claim_boundary": {
            "auditable_responsibility_shift_claimed": True,
            "numeric_productivity_claimed": False,
            "developer_hours_saved_claimed": False,
            "universal_no_native_extension_claimed": False,
            "v4_eliminates_all_cuda_or_optix_expertise_claimed": False,
        },
    }


def main() -> None:
    pins = verify_pins()
    claim_matrix = build_claim_matrix(pins)
    ledger = build_programming_ledger()
    dump(HISTORY / "goal5787_cgo_claim_matrix_20260816.json", claim_matrix)
    dump(HISTORY / "goal5787_programming_responsibility_ledger_20260816.json", ledger)
    print(json.dumps({
        "status": "PASS",
        "verified_authority_count": len(pins),
        "claim_row_count": len(claim_matrix["performance"]["rows"]),
        "application_ledger_count": len(ledger["applications"]),
        "ci_split": claim_matrix["performance"]["ci_split"],
        "new_performance_claimed": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
