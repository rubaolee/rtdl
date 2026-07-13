#!/usr/bin/env python3
"""Build the Goal5434 Water/BG external action packet."""

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
GOAL5431 = RESULTS / "xhd_goal5431_water_bg_outbox_refresh.json"
GOAL5432 = RESULTS / "xhd_goal5432_public_artifact_live_refresh.json"
GOAL5433 = RESULTS / "xhd_goal5433_water_bg_external_response_classifier_contract.json"
ACTION_PACKET = REQUESTS / "water_bg_external_action_packet.md"
OUT = RESULTS / "xhd_goal5434_water_bg_external_action_packet.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _b(value: Any) -> str:
    return str(bool(value)).lower()


def _build_markdown(goal5430: dict[str, Any], goal5431: dict[str, Any], goal5432: dict[str, Any], goal5433: dict[str, Any]) -> str:
    case = goal5430["case"]
    water = goal5430["public_reconstruction_evidence"]["waterbodies"]
    bg = goal5430["public_reconstruction_evidence"]["blockgroups"]
    outbox = {row["message_id"]: row["path"].replace("\\", "/") for row in goal5431["outbox_files"]}
    current_hashes = goal5433["current_public_hashes"]
    return dedent(
        f"""\
        # X-HD WaterBodies/BG External Action Packet

        Status: `prepared_not_sent`

        This packet is the single entry point for the next X-HD
        WaterBodies->BlockGroups external action. It packages what to send, how
        to normalize any response, how to classify the response, and what is
        still forbidden.

        ## Current State

        ```text
        case_id = {case["case_id"]}
        paper_pair = {case["paper_pair"]}
        input_identity_level = {case["input_identity_level"]}
        author paper-config num_points_cell = {case["paper_config"]["num_points_cell"]}
        author paper-config HDResult = {case["paper_config"]["hd_result"]}
        RTDL exact-witness HDResult = {case["rtdl_exact_witness"]["hd_result_float64"]}
        abs diff = {case["rtdl_exact_witness"]["abs_diff_vs_author"]} <= {case["rtdl_exact_witness"]["comparison_tolerance"]}
        per_source_witness_exact = {_b(case["rtdl_exact_witness"]["per_source_witness_exact"])}
        ```

        This is strong Level-B public-reconstruction evidence. It is **not** exact
        paper input reproduction.

        ## Current Public Reconstruction Hashes

        ```text
        USADetailedWaterBodies.wkt =
        {current_hashes["USADetailedWaterBodies.wkt"]}

        USACensusBlockGroupBoundaries.wkt =
        {current_hashes["USACensusBlockGroupBoundaries.wkt"]}
        ```

        WaterBodies details:

        ```text
        service_item_id = {water["service_item_id"]}
        service_url = {water["service_url"]}
        point_count_delta = {water["point_count_delta"]}
        max_abs_mbr_delta = {water["max_abs_mbr_delta"]}
        ```

        BlockGroups details:

        ```text
        service_item_id = {bg["service_item_id"]}
        service_url = {bg["service_url"]}
        point_count_delta = {bg["point_count_delta"]}
        max_abs_mbr_delta = {bg["max_abs_mbr_delta"]}
        ```

        ## Public Artifact Refresh

        Goal5432 status:

        ```text
        {goal5432["status"]}
        new_public_exact_input_artifact_found = {_b(goal5432["classification"]["new_public_exact_input_artifact_found"])}
        acm_supplement_inspected = {_b(goal5432["classification"]["acm_supplement_inspected"])}
        exact_input_blocker_removed = {_b(goal5432["classification"]["exact_input_blocker_removed"])}
        ```

        Interpretation:

        ```text
        No public exact input path is currently known.
        ACM supplement bytes were not downloaded, so the supplement is not
        inspected.
        ```

        ## What To Send Or Review

        Author/artifact-owner request:

        ```text
        {outbox["author_water_bg_input_hash_request"]}
        ```

        Exact-equivalence review request:

        ```text
        {outbox["water_bg_exact_equivalence_review_request"]}
        ```

        Both drafts are `prepared_not_sent`. Sending is an owner/external action,
        not a claim that a response exists.

        ## If A Response Arrives

        1. Save a normalized metadata record with:

        ```text
        Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
        ```

        2. If the response contains private material, store only minimal metadata
        in the repository unless the sender permits committing raw text.

        3. Classify it:

        ```text
        py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py --input <response.json> --output <classified.json>
        ```

        4. Follow the classifier `recommended_next_action`. Do not improvise a
        stronger claim.

        ## Positive Classifications

        ```text
        author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim
        author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate
        byte_identical_regeneration_available__run_regeneration_then_hash_gate
        acm_supplement_contains_possible_provenance__map_before_route
        exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix
        ```

        Even these positive classifications do **not** directly authorize exact
        paper reproduction wording. They authorize the next gate.

        ## Fail-Closed Cases

        Keep Level-B if:

        ```text
        one of the required WKT paths is missing
        hashes do not match current public reconstruction
        response type is unknown or underspecified
        exact-equivalence verdict is not Water/BG scoped
        exact-equivalence verdict lacks an accepted claim name
        response says artifacts are unavailable
        ```

        ## Claim Boundary

        Authorized:

        ```text
        external_action_packet_prepared = true
        ```

        Not authorized:

        ```text
        request_sent_claimed = false
        external_response_received = false
        external_artifacts_acquired = false
        exact_equivalence_accepted = false
        exact_paper_dataset_reproduction_claimed = false
        figure5_reproduction_claimed = false
        full_xhd_paper_reproduction_claimed = false
        performance_ratio_claimed = false
        pod_execution_claimed = false
        new_rtdl_route_code_added = false
        explicit_lb_reopened = false
        route_micro_optimization_goal_authorized = false
        ```

        ## Stop-Loss Rule

        This packet does not reopen row/hash/offload-stream implementation work.
        It only packages external action and response classification.

        ```text
        gate_generic_capability_produced: true
        gate_non_app_consumer: external action packet / response classification workflow
        gate_requires_app_specific_logic: false
        gate_downstream_consumer_reachable: true
        ```
        """
    ).lstrip()


def build_payload() -> dict[str, Any]:
    goal5430 = _load(GOAL5430)
    goal5431 = _load(GOAL5431)
    goal5432 = _load(GOAL5432)
    goal5433 = _load(GOAL5433)
    REQUESTS.mkdir(parents=True, exist_ok=True)
    ACTION_PACKET.write_text(_build_markdown(goal5430, goal5431, goal5432, goal5433), encoding="utf-8")
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5434.water_bg_external_action_packet.v1",
        "goal": "Goal5434",
        "date": "2026-07-10",
        "status": "water_bg_external_action_packet_ready__prepared_not_sent",
        "purpose": "Create a single action packet for Water/BG external request/review/response classification.",
        "action_packet": _rel(ACTION_PACKET),
        "inputs": {
            "goal5430": _rel(GOAL5430),
            "goal5431": _rel(GOAL5431),
            "goal5432": _rel(GOAL5432),
            "goal5433": _rel(GOAL5433),
        },
        "included_workflow": {
            "send_or_review_author_request": "Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md",
            "send_or_review_exact_equivalence_request": "Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md",
            "normalize_response_template": "Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json",
            "classify_response_script": "Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py",
        },
        "claim_boundary": {
            "external_action_packet_prepared": True,
            "request_sent_claimed": False,
            "external_response_received": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external action packet / response classification workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: packaging external action, not app-artifact parity implementation.",
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "External action packet only. POD is expected only after a positive classifier outcome.",
        },
        "next_action": "send_or_review_action_packet_and_await_classified_external_response",
        "allowed_summary": (
            "Goal5434 creates a single Water/BG external action packet. It does not send requests, "
            "receive responses, accept exact-equivalence, acquire artifacts, run POD, or change X-HD claim status."
        ),
        "not_allowed": [
            "claiming the action packet was sent",
            "claiming any response arrived",
            "claiming external artifacts were acquired",
            "claiming exact-equivalence was accepted",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 reproduction",
            "claiming full X-HD paper reproduction",
            "claiming author-vs-RTDL performance ratio",
            "starting POD/route work before a positive classifier outcome",
        ],
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "action_packet": payload["action_packet"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
