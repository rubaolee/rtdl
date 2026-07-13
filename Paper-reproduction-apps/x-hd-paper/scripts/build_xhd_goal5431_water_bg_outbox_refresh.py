#!/usr/bin/env python3
"""Build Goal5431 Water/BG send-ready outbox drafts from Goal5430."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
REQUESTS = APP / "requests"
GOAL5430 = RESULTS / "xhd_goal5430_water_bg_exact_equivalence_packet.json"
AUTHOR_DRAFT = REQUESTS / "author_water_bg_input_hash_request.md"
REVIEW_DRAFT = REQUESTS / "water_bg_exact_equivalence_review_request.md"
OUT = RESULTS / "xhd_goal5431_water_bg_outbox_refresh.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_float(value: float) -> str:
    return f"{value:.17g}"


def _author_draft(packet: dict[str, Any]) -> str:
    request = packet["author_artifact_request"]
    case = packet["case"]
    evidence = packet["public_reconstruction_evidence"]
    water = evidence["waterbodies"]
    blockgroups = evidence["blockgroups"]
    body = "\n".join(f"        {i + 1}. {item}" for i, item in enumerate(request["request_items"]))
    return dedent(
        f"""\
        # Draft: X-HD WaterBodies/BG Author Input Hash Request

        Status: `prepared_not_sent`

        Suggested recipients:

        ```text
        X-HD authors / artifact owner
        ```

        Subject:

        ```text
        X-HD reproduction: WaterBodies/BG paper input hashes or regeneration provenance
        ```

        Body:

        ```text
        Hello,

        We are reproducing the X-HD paper's WaterBodies -> BlockGroups case.
        Our current public ArcGIS reconstruction is a strong Level-B candidate,
        but we cannot claim exact paper reproduction without paper-run input
        hashes, bytes, or byte-identical regeneration provenance.

        Current evidence:

        - Paper pair: {case["paper_pair"]}
        - Paper config: num_points_cell={case["paper_config"]["num_points_cell"]}
        - Author paper-config HDResult: {_fmt_float(case["paper_config"]["hd_result"])}
        - RTDL exact-witness HDResult (float64): {_fmt_float(case["rtdl_exact_witness"]["hd_result_float64"])}
        - RTDL vs author abs diff: {_fmt_float(case["rtdl_exact_witness"]["abs_diff_vs_author"])} <= {_fmt_float(case["rtdl_exact_witness"]["comparison_tolerance"])}
        - WaterBodies public WKT sha256: {water["generated_wkt_sha256"]}
        - BlockGroups public WKT sha256: {blockgroups["generated_wkt_sha256"]}
        - WaterBodies point-count delta vs paper log: {water["point_count_delta"]}
        - BlockGroups point-count delta vs paper log: {blockgroups["point_count_delta"]}

        Could you provide, or confirm availability of:

        {body}

        If the files cannot be shared, hashes plus exact source snapshots,
        export parameters, and conversion details would still let us classify
        the reproduction boundary accurately without overclaiming exact paper
        reproduction.

        Thank you.
        ```

        Claim boundary:

        ```text
        This draft is not sent.
        No external artifacts are claimed acquired.
        No exact paper dataset claim is made.
        ```
        """
    ).lstrip().replace("\n        1.", "\n1.")


def _review_draft(packet: dict[str, Any]) -> str:
    review = packet["external_exact_equivalence_review_packet"]
    evidence = packet["public_reconstruction_evidence"]
    water = evidence["waterbodies"]
    blockgroups = evidence["blockgroups"]
    for_acceptance = "\n".join(f"        {i + 1}. {item}" for i, item in enumerate(review["evidence_for_acceptance"]))
    against = "\n".join(f"        {i + 1}. {item}" for i, item in enumerate(review["evidence_against_acceptance"]))
    outcomes = "\n".join(f"        {i + 1}. {item}" for i, item in enumerate(review["allowed_review_outcomes"]))
    return dedent(
        f"""\
        # Draft: WaterBodies/BG Exact-Equivalence Review Request

        Status: `prepared_not_sent`

        Suggested recipient:

        ```text
        owner or external reviewer
        ```

        Subject:

        ```text
        X-HD WaterBodies/BG exact-equivalence decision request
        ```

        Review question:

        ```text
        {review["question"]}
        ```

        Evidence supporting possible acceptance:

        ```text
        {for_acceptance}
        ```

        Evidence against exact self-promotion:

        ```text
        {against}
        ```

        Concrete public reconstruction identifiers:

        ```text
        WaterBodies service item: {water["service_item_id"]}
        WaterBodies service URL: {water["service_url"]}
        WaterBodies generated WKT sha256: {water["generated_wkt_sha256"]}
        WaterBodies point-count delta: {water["point_count_delta"]}
        WaterBodies max_abs_mbr_delta: {_fmt_float(water["max_abs_mbr_delta"])}

        BlockGroups service item: {blockgroups["service_item_id"]}
        BlockGroups service URL: {blockgroups["service_url"]}
        BlockGroups generated WKT sha256: {blockgroups["generated_wkt_sha256"]}
        BlockGroups point-count delta: {blockgroups["point_count_delta"]}
        BlockGroups max_abs_mbr_delta: {_fmt_float(blockgroups["max_abs_mbr_delta"])}
        ```

        Allowed answers:

        ```text
        {outcomes}
        ```

        Default without explicit acceptance:

        ```text
        {review["recommended_default_without_external_acceptance"]}
        ```

        Claim boundary:

        ```text
        This draft is not sent.
        Exact-equivalence is not accepted unless a reviewer explicitly says so.
        Point counts, MBRs, and HDResult alone are not treated as proof of exact paper input identity.
        ```
        """
    ).lstrip().replace("\n        1.", "\n1.")


def build_payload() -> dict[str, Any]:
    packet = _load(GOAL5430)
    REQUESTS.mkdir(parents=True, exist_ok=True)
    author_text = _author_draft(packet)
    review_text = _review_draft(packet)
    AUTHOR_DRAFT.write_text(author_text, encoding="utf-8")
    REVIEW_DRAFT.write_text(review_text, encoding="utf-8")

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5431.water_bg_outbox_refresh.v1",
        "goal": "Goal5431",
        "date": "2026-07-10",
        "status": "water_bg_outbox_refreshed_from_goal5430__prepared_not_sent",
        "source_goal": "Goal5430",
        "outbox_files": [
            {
                "message_id": "author_water_bg_input_hash_request",
                "path": str(AUTHOR_DRAFT.relative_to(ROOT)),
                "target": "X-HD authors / artifact owner",
                "send_status": "prepared_not_sent",
            },
            {
                "message_id": "water_bg_exact_equivalence_review_request",
                "path": str(REVIEW_DRAFT.relative_to(ROOT)),
                "target": "owner or external reviewer",
                "send_status": "prepared_not_sent",
            },
        ],
        "claim_boundary": {
            "outbox_refreshed": True,
            "request_sent_claimed": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "new_pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "send-ready author artifact request and exact-equivalence review request drafts",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: no app-artifact parity implementation; this only prepares external decision messages.",
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Sending or reviewing requests is not a POD task. POD becomes useful after a positive external response.",
        },
        "next_action": "owner_or_external_reviewer_can_send_or_review_the_prepared_drafts",
        "allowed_summary": (
            "Goal5431 refreshes the WaterBodies/BG request outbox with Goal5430 evidence. "
            "The drafts are prepared but not sent, and no exact-equivalence or artifact acquisition is claimed."
        ),
        "not_allowed": [
            "claiming either request was sent",
            "claiming any recipient responded",
            "claiming exact-equivalence was accepted",
            "claiming external artifacts were acquired",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 reproduction",
            "claiming full X-HD paper reproduction",
            "claiming author-vs-RTDL performance ratio",
        ],
        "source_artifacts": {
            "goal5430": str(GOAL5430),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "outbox_files": len(payload["outbox_files"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
