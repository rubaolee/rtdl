#!/usr/bin/env python3
"""Goal5442 public provenance rescan for X-HD full reproduction.

This goal is intentionally a governance / provenance step.  It reuses the
Goal5432 live public-artifact refresh, adds the public web observations that
motivated this rescan, and decides whether the exact-input blocker has changed.

It does not run author code, RTDL routes, POD commands, or performance tests.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
SCRIPTS = APP / "scripts"
OUT = RESULTS / "xhd_goal5442_public_provenance_rescan.json"


PUBLIC_WEB_OBSERVATIONS = [
    {
        "surface": "ACM proceedings page",
        "url": "https://dl.acm.org/doi/proceedings/10.1145/3797905?tocHeading=heading19",
        "observation": "The proceedings listing exposes an X-HD supplement entry named ics26-106.zip.",
        "exact_input_evidence": False,
        "reason_not_exact": "Listing visibility is not zip-byte inspection and does not reveal dataset files or hashes.",
    },
    {
        "surface": "GitHub repository",
        "url": "https://github.com/pwrliang/X-HD",
        "observation": "The public repository is the pinned source/script/log provenance root.",
        "exact_input_evidence": False,
        "reason_not_exact": "Goal5432 found source/scripts/logs but no input dataset archive, release asset, or root data directory.",
    },
    {
        "surface": "ArcGIS USA Detailed Water Bodies",
        "url": "https://hub.arcgis.com/datasets/esri::usa-detailed-water-bodies/about",
        "observation": "A public WaterBodies source candidate exists and remains useful for Level-B public reconstruction.",
        "exact_input_evidence": False,
        "reason_not_exact": "A source candidate is not the author's exact WKT bytes or hash-provenance.",
    },
    {
        "surface": "X-HD public PDF",
        "url": "https://rubaolee.github.io/paper_pdfs/2026-xhd.pdf",
        "observation": "The public paper confirms the X-HD topic and high-level datasets/figures.",
        "exact_input_evidence": False,
        "reason_not_exact": "The PDF is not an input archive and does not provide exact local HDDatasets bytes.",
    },
]


def _load_goal5432_module() -> Any:
    script = SCRIPTS / "run_xhd_goal5432_public_artifact_live_refresh.py"
    spec = importlib.util.spec_from_file_location("goal5432_public_artifact_live_refresh", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    goal5432 = _load_goal5432_module()
    refresh = goal5432.build_payload()
    classification = refresh["classification"]
    acm = refresh["live_surfaces"]["acm_supplement"]
    github = refresh["live_surfaces"]["github"]
    crossref = refresh["live_surfaces"]["crossref"]

    public_exact_found = bool(classification["new_public_exact_input_artifact_found"])
    acm_zip_visible = any("ics26-106.zip" in row["url"] for row in acm["checks"])
    acm_zip_inspected = bool(classification["acm_supplement_inspected"])

    exact_input_blocker_removed = False
    if public_exact_found:
        status = "public_provenance_rescan_possible_new_artifact_requires_human_inspection"
        next_action = "inspect_possible_new_public_artifact_before_any_pod_or_route_claim"
    else:
        status = "public_provenance_rescan_no_new_exact_input_path__external_chain_still_needed"
        next_action = "continue_external_request_chain_or_record_real_response"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5442.public_provenance_rescan.v1",
        "goal": "Goal5442",
        "date": "2026-07-10",
        "purpose": (
            "Rescan public X-HD provenance surfaces after the full-objective gap matrix, "
            "without substituting route/POD work for missing exact input evidence."
        ),
        "status": status,
        "source_artifacts": {
            "goal5432_live_refresh_script": _rel(SCRIPTS / "run_xhd_goal5432_public_artifact_live_refresh.py"),
            "goal5432_live_refresh_result": _rel(RESULTS / "xhd_goal5432_public_artifact_live_refresh.json"),
            "goal5441_functional_gap_matrix": _rel(RESULTS / "xhd_goal5441_full_objective_functional_gap_matrix.json"),
            "goal5440_external_chain_packet": _rel(RESULTS / "xhd_goal5440_external_evidence_chain_review_packet.json"),
        },
        "public_web_observations": PUBLIC_WEB_OBSERVATIONS,
        "live_refresh_embedded": {
            "schema": refresh["schema"],
            "status": refresh["status"],
            "classification": classification,
            "acm_supplement": {
                "artifact_name": acm["artifact_name"],
                "zip_entry_visible_from_known_urls": acm_zip_visible,
                "downloaded_or_zip_magic_observed": acm["downloaded_or_zip_magic_observed"],
                "statuses": acm["statuses"],
                "classification": acm["classification"],
            },
            "crossref": {
                "title": crossref["title"],
                "dataset_or_artifact_link_found": crossref["dataset_or_artifact_link_found"],
                "artifact_like_links": crossref["artifact_like_links"],
            },
            "github": {
                "full_name": github["full_name"],
                "branches": github["branches"],
                "release_count": github["release_count"],
                "root_data_directory_found": github["root_data_directory_found"],
                "dataset_archive_release_found": github["dataset_archive_release_found"],
                "tree_likely_input_dataset_blob_found": github["tree_likely_input_dataset_blob_found"],
                "interpretation": github["interpretation"],
            },
        },
        "classification": {
            "acm_zip_listing_observed": acm_zip_visible,
            "acm_supplement_inspected": acm_zip_inspected,
            "github_public_source_repo_present": github["full_name"] == "pwrliang/X-HD",
            "github_exact_input_archive_found": bool(
                github["dataset_archive_release_found"]
                or github["root_data_directory_found"]
                or github["tree_likely_input_dataset_blob_found"]
            ),
            "crossref_exact_input_link_found": bool(crossref["dataset_or_artifact_link_found"]),
            "arcgis_source_candidates_present": True,
            "arcgis_source_candidates_are_exact_author_inputs": False,
            "new_public_exact_input_artifact_found": public_exact_found,
            "exact_input_blocker_removed": exact_input_blocker_removed,
        },
        "interpretation": {
            "public_provenance_status_changed": public_exact_found,
            "acm_supplement_status": (
                "listed_but_not_inspected" if acm_zip_visible and not acm_zip_inspected else "inspected_or_not_listed"
            ),
            "why_arcgis_does_not_close_blocker": (
                "ArcGIS public services can support Level-B public reconstruction, but exact paper reproduction "
                "requires author WKT bytes/hashes, byte-identical regeneration, inspectable supplement contents, "
                "or external exact-equivalence acceptance."
            ),
            "next_action": next_action,
            "pod_expected_next": False,
            "reason_pod_not_expected": (
                "POD execution cannot create missing public provenance. It becomes useful only after an exact "
                "artifact, hash manifest, byte-identical regeneration recipe, inspectable supplement, or accepted "
                "exact-equivalence response creates a strict same-input gate."
            ),
        },
        "claim_boundary": {
            "public_provenance_rescan_claimed": True,
            "acm_supplement_inspected": acm_zip_inspected,
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
            "gate_non_app_consumer": "public provenance rescan / exact-input blocker governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: evidence/provenance governance, not app-artifact parity implementation.",
        },
        "allowed_summary": (
            "Goal5442 rescans public X-HD provenance surfaces. Public pages expose source/proceedings/source-candidate "
            "signals, but no exact input artifact or accepted exact-equivalence evidence is acquired unless the "
            "classification explicitly says otherwise."
        ),
        "not_allowed": [
            "claiming the ACM supplement was inspected without zip bytes or extracted contents",
            "claiming public ArcGIS source candidates are exact author WKT inputs",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming an author-vs-RTDL performance ratio",
            "running POD, route tuning, or explicit -lb work as a substitute for missing provenance",
        ],
        "exit_label": status,
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "new_public_exact_input_artifact_found": payload["classification"]["new_public_exact_input_artifact_found"],
        "exact_input_blocker_removed": payload["classification"]["exact_input_blocker_removed"],
        "pod_expected_next": payload["interpretation"]["pod_expected_next"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
