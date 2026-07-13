#!/usr/bin/env python3
"""Goal5432 live public artifact refresh for X-HD exact-input provenance."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5432_public_artifact_live_refresh.json"

DOI = "10.1145/3797905.3800509"
ACM_SUPPLEMENT_URLS = [
    "https://dl.acm.org/action/downloadSupplement?doi=10.1145%2F3797905.3800509&file=ics26-106.zip",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=true",
]
CROSSREF_URL = f"https://api.crossref.org/works/{DOI}"
GITHUB_API = "https://api.github.com/repos/pwrliang/X-HD"
AUTHOR_PAGE_URLS = [
    "https://rubaolee.github.io/paper_pdfs/2026-xhd.pdf",
    "https://gengl.me/publications/ics26/",
]

DATASET_TERMS = (
    "hddatasets",
    "dataset",
    "datasets",
    "data/",
    ".zip",
    ".tar",
    ".tgz",
    ".tar.gz",
    ".7z",
    ".wkt",
    ".ply",
    ".nii",
    ".nifti",
)


def _request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    hdrs = {
        "User-Agent": "RTDL-XHD-Provenance-Refresh/5432 (+https://github.com/pwrliang/X-HD)",
        "Accept": "*/*",
    }
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, method=method, headers=hdrs)
    started = time.perf_counter()
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            body = resp.read()
            elapsed = time.perf_counter() - started
            return {
                "ok": 200 <= resp.status < 300,
                "status": resp.status,
                "url": resp.geturl(),
                "content_type": resp.headers.get("content-type"),
                "content_length_header": resp.headers.get("content-length"),
                "elapsed_sec": elapsed,
                "body": body,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        body = exc.read() if exc.fp is not None else b""
        return {
            "ok": False,
            "status": exc.code,
            "url": url,
            "content_type": exc.headers.get("content-type") if exc.headers else None,
            "content_length_header": exc.headers.get("content-length") if exc.headers else None,
            "elapsed_sec": elapsed,
            "body": body,
            "error": f"HTTPError: {exc.reason}",
        }
    except Exception as exc:  # noqa: BLE001 - recorded as evidence, not suppressed.
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "status": None,
            "url": url,
            "content_type": None,
            "content_length_header": None,
            "elapsed_sec": elapsed,
            "body": b"",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _public_entry(resp: dict[str, Any]) -> dict[str, Any]:
    body = resp.pop("body", b"")
    return {
        **resp,
        "body_bytes": len(body),
        "body_prefix_hex": body[:16].hex(),
        "zip_magic_observed": body.startswith(b"PK\x03\x04"),
    }


def _json_get(url: str) -> tuple[dict[str, Any], dict[str, Any] | list[Any] | None]:
    resp = _request(url)
    body = resp["body"]
    public = _public_entry(resp)
    if public["ok"] and body:
        try:
            return public, json.loads(body.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            public["json_error"] = f"{type(exc).__name__}: {exc}"
    return public, None


def _probe_acm() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for url in ACM_SUPPLEMENT_URLS:
        head = _public_entry(_request(url, method="HEAD"))
        ranged = _public_entry(_request(url, headers={"Range": "bytes=0-3"}))
        checks.append({"url": url, "head": head, "range_get": ranged})
    downloaded = any(row["range_get"]["ok"] and row["range_get"]["zip_magic_observed"] for row in checks)
    statuses = [row["head"]["status"] for row in checks] + [row["range_get"]["status"] for row in checks]
    return {
        "artifact_name": "ics26-106.zip",
        "checks": checks,
        "downloaded_or_zip_magic_observed": downloaded,
        "statuses": statuses,
        "classification": "acm_supplement_inspected" if downloaded else "acm_supplement_visible_but_not_downloaded_from_current_environment",
    }


def _probe_crossref() -> dict[str, Any]:
    resp, payload = _json_get(CROSSREF_URL)
    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    links = message.get("link", []) if isinstance(message, dict) else []
    relations = message.get("relation", {}) if isinstance(message, dict) else {}
    artifact_links = [
        link for link in links
        if any(term in str(link.get("URL", "")).lower() for term in ("zip", "dataset", "data", "supp"))
    ]
    return {
        "url": CROSSREF_URL,
        "response": resp,
        "title": (message.get("title") or [None])[0] if isinstance(message, dict) else None,
        "doi": message.get("DOI") if isinstance(message, dict) else None,
        "link_count": len(links),
        "links": links,
        "relation_keys": sorted(relations.keys()) if isinstance(relations, dict) else [],
        "archive": message.get("archive", []) if isinstance(message, dict) else [],
        "dataset_or_artifact_link_found": bool(artifact_links),
        "artifact_like_links": artifact_links,
    }


def _probe_github() -> dict[str, Any]:
    repo_resp, repo_payload = _json_get(GITHUB_API)
    releases_resp, releases_payload = _json_get(f"{GITHUB_API}/releases")
    contents_resp, contents_payload = _json_get(f"{GITHUB_API}/contents")
    branches_resp, branches_payload = _json_get(f"{GITHUB_API}/branches")
    tree_resp, tree_payload = _json_get(f"{GITHUB_API}/git/trees/main?recursive=1")

    contents = contents_payload if isinstance(contents_payload, list) else []
    root_entries = [f"{row.get('name')}/" if row.get("type") == "dir" else row.get("name") for row in contents]
    root_data = [
        row for row in contents
        if row.get("type") == "dir" and row.get("name", "").lower() in {"data", "dataset", "datasets", "hddatasets"}
    ]

    releases = releases_payload if isinstance(releases_payload, list) else []
    release_assets: list[dict[str, Any]] = []
    for release in releases:
        for asset in release.get("assets", []):
            release_assets.append({
                "release": release.get("tag_name"),
                "name": asset.get("name"),
                "browser_download_url": asset.get("browser_download_url"),
                "size": asset.get("size"),
            })
    dataset_assets = [
        asset for asset in release_assets
        if any(term in str(asset.get("name", "")).lower() for term in ("data", "dataset", "hddataset", "zip", "tar"))
    ]

    branches = {}
    if isinstance(branches_payload, list):
        branches = {row.get("name"): row.get("commit", {}).get("sha") for row in branches_payload}

    tree = tree_payload.get("tree", []) if isinstance(tree_payload, dict) else []
    matches = []
    for item in tree:
        path = item.get("path", "")
        low = path.lower()
        if any(term in low for term in DATASET_TERMS):
            matches.append({"path": path, "type": item.get("type"), "size": item.get("size")})
    likely_data_blobs = [
        row for row in matches
        if not str(row["path"]).startswith("expr/logs/")
        and not str(row["path"]).startswith("expr/for_the_paper/logs/")
        and any(term in str(row["path"]).lower() for term in ("hddatasets", "dataset", "data/", ".zip", ".tar", ".tgz", ".7z"))
    ]

    return {
        "repo_response": repo_resp,
        "full_name": repo_payload.get("full_name") if isinstance(repo_payload, dict) else None,
        "default_branch": repo_payload.get("default_branch") if isinstance(repo_payload, dict) else None,
        "pushed_at": repo_payload.get("pushed_at") if isinstance(repo_payload, dict) else None,
        "branches_response": branches_resp,
        "branches": branches,
        "releases_response": releases_resp,
        "release_count": len(releases),
        "release_assets": release_assets,
        "dataset_archive_release_found": bool(dataset_assets),
        "dataset_like_release_assets": dataset_assets,
        "contents_response": contents_resp,
        "top_level_contents": root_entries,
        "root_data_directory_found": bool(root_data),
        "tree_response": tree_resp,
        "tree_path_count": len(tree),
        "tree_dataset_like_match_count": len(matches),
        "tree_paths_matching_dataset_or_archive_terms": matches[:80],
        "tree_likely_input_dataset_blob_found": bool(likely_data_blobs),
        "tree_likely_input_dataset_blobs": likely_data_blobs[:40],
        "interpretation": "source_scripts_logs_only_no_input_dataset_blob_or_release" if not (root_data or dataset_assets or likely_data_blobs) else "possible_public_dataset_artifact_requires_inspection",
    }


def _probe_author_pages() -> list[dict[str, Any]]:
    rows = []
    for url in AUTHOR_PAGE_URLS:
        resp = _request(url, headers={"Range": "bytes=0-2047"})
        body = resp["body"]
        public = _public_entry(resp)
        lower = body[:4096].decode("utf-8", errors="ignore").lower()
        rows.append({
            "url": url,
            "response": public,
            "mentions_dataset_terms_in_prefix": any(term in lower for term in ("hddatasets", "dataset", "supplement", "zenodo", "figshare", "osf")),
            "mentions_github_xhd_in_prefix": "github.com/pwrliang/x-hd" in lower,
        })
    return rows


def build_payload() -> dict[str, Any]:
    acm = _probe_acm()
    crossref = _probe_crossref()
    github = _probe_github()
    author_pages = _probe_author_pages()

    new_exact_artifact = (
        acm["downloaded_or_zip_magic_observed"]
        or crossref["dataset_or_artifact_link_found"]
        or github["dataset_archive_release_found"]
        or github["root_data_directory_found"]
        or github["tree_likely_input_dataset_blob_found"]
    )
    acm_inspected = acm["downloaded_or_zip_magic_observed"]

    if new_exact_artifact:
        status = "public_artifact_refresh_possible_new_artifact_requires_human_inspection"
        exit_label = "public_artifact_refresh_possible_new_artifact_requires_human_inspection"
    else:
        status = "public_artifact_refresh_no_new_exact_input_path__acm_supplement_still_uninspected"
        exit_label = "public_artifact_refresh_no_new_exact_input_path__external_response_chain_still_needed"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5432.public_artifact_live_refresh.v1",
        "goal": "Goal5432",
        "date": "2026-07-10",
        "purpose": "Live refresh public artifact/provenance surfaces after the Water/BG outbox was prepared, before doing more route or POD work.",
        "status": status,
        "input_context": {
            "previous_artifact_sweeps": [
                "Goal5325",
                "Goal5327",
                "Goal5334",
                "Goal5346",
            ],
            "current_outbox_goal": "Goal5431",
            "current_strongest_candidate": "WaterBodies->BlockGroups Level-B public reconstruction, not exact paper input",
        },
        "live_surfaces": {
            "acm_supplement": acm,
            "crossref": crossref,
            "github": github,
            "author_pages": author_pages,
        },
        "classification": {
            "new_public_exact_input_artifact_found": new_exact_artifact,
            "acm_supplement_inspected": acm_inspected,
            "external_artifacts_acquired": False,
            "exact_input_blocker_removed": False,
            "github_has_release_assets": github["release_count"] > 0,
            "github_has_dataset_archive_release": github["dataset_archive_release_found"],
            "github_has_root_data_directory": github["root_data_directory_found"],
            "github_has_likely_input_dataset_blob": github["tree_likely_input_dataset_blob_found"],
            "crossref_has_dataset_or_artifact_link": crossref["dataset_or_artifact_link_found"],
        },
        "interpretation": {
            "current_public_artifact_status_changed": new_exact_artifact,
            "next_action": (
                "inspect_possible_new_artifact_before_any_claim"
                if new_exact_artifact
                else "send_or_review_goal5431_outbox_or_wait_for_external_author_acm_response"
            ),
            "pod_expected_next": False,
            "reason_pod_not_expected": "POD cannot create missing public provenance. It becomes useful only after exact artifacts, hashes, byte-identical regeneration, or explicit exact-equivalence acceptance appears.",
        },
        "claim_boundary": {
            "public_artifact_refresh_claimed": True,
            "new_public_exact_input_artifact_found": new_exact_artifact,
            "acm_supplement_inspected": acm_inspected,
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
            "gate_non_app_consumer": "public artifact availability refresh / external provenance decision",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: provenance refresh, not app-artifact parity implementation.",
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Public metadata / artifact refresh only.",
        },
        "allowed_summary": (
            "Goal5432 refreshes public X-HD artifact surfaces. No new public exact-input path was found "
            "unless the result classification explicitly says otherwise; ACM supplement access remains unresolved if not inspected."
        ),
        "not_allowed": [
            "claiming the ACM supplement has been inspected unless zip bytes were downloaded",
            "claiming the ACM supplement contains datasets without inspection",
            "claiming the ACM supplement contains no useful artifacts without inspection",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 reproduction",
            "claiming full X-HD paper reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running route/POD work as a substitute for missing provenance",
        ],
        "exit_label": exit_label,
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "new_public_exact_input_artifact_found": payload["classification"]["new_public_exact_input_artifact_found"],
        "acm_supplement_inspected": payload["classification"]["acm_supplement_inspected"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
