#!/usr/bin/env python3
"""Goal5449 deeper public mirror/provenance probe for X-HD exact inputs.

This extends Goal5442 by probing public surfaces that were not part of the
shallow rescan: GitHub non-tree metadata, branch-specific raw/data paths, public
data-index APIs, and extra ACM URL variants.  It records evidence only; it does
not run POD, author code, or RTDL routes.
"""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5449_deep_public_mirror_probe.json"

DOI = "10.1145/3797905.3800509"
REPO_API = "https://api.github.com/repos/pwrliang/X-HD"
BRANCHES = {
    "main": "7bf41c8442d059c94f4178355c6d5a10571d9658",
    "paper": "8c3846866052e1e8755210021f23fac2cbe8c3d6",
    "hybrid": "4d9046a9e55d87f35daf81dd718444029fab56ce",
}

DATA_PATH_CANDIDATES = [
    "HDDatasets",
    "HDDatasets/README.md",
    "data",
    "data/README.md",
    "dataset",
    "dataset/README.md",
    "datasets",
    "datasets/README.md",
    "inputs",
    "inputs/README.md",
    "artifact",
    "artifact/README.md",
    "artifacts",
    "artifacts/README.md",
]

ACM_URL_VARIANTS = [
    f"https://dl.acm.org/action/downloadSupplement?doi={urllib.parse.quote(DOI, safe='')}&file=ics26-106.zip",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=true",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=1",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=true&download=true",
]

REGISTRY_URLS = {
    "crossref_work": f"https://api.crossref.org/works/{DOI}",
    "datacite_query": "https://api.datacite.org/dois?query=" + urllib.parse.quote(
        '"X-HD" "Fast Hausdorff Distance"'
    ),
    "zenodo_query": "https://zenodo.org/api/records?q=" + urllib.parse.quote(
        '"X-HD" "Hausdorff" "Ray Tracing"'
    ),
    "openalex_work": "https://api.openalex.org/works/doi:" + urllib.parse.quote(DOI, safe=""),
}

ARTIFACT_TERMS = (
    "hddatasets",
    "dataset",
    "datasets",
    "input",
    "inputs",
    "artifact",
    "supplement",
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

LOG_PREFIXES = (
    "expr/logs/",
    "expr/for_the_paper/logs/",
    "expr/logs_v",
)

SOURCE_PREFIXES = (
    "src/",
    "cmake/",
    "thirdparty/",
)

SOURCE_SUFFIXES = (
    ".h",
    ".hpp",
    ".hh",
    ".cc",
    ".cpp",
    ".cu",
    ".cuh",
    ".cmake",
    ".txt",
    ".md",
)

DATA_FILE_SUFFIXES = (
    ".zip",
    ".tar",
    ".tgz",
    ".tar.gz",
    ".7z",
    ".wkt",
    ".ply",
    ".nii",
    ".nii.gz",
    ".nifti",
    ".bz2",
)

XHD_RELEVANCE_TERMS = (
    "x-hd",
    "fast hausdorff distance computation with ray tracing",
    "pwrliang/x-hd",
    "10.1145/3797905.3800509",
)


def _request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    timeout: float = 20.0,
    max_body: int = 5_000_000,
) -> dict[str, Any]:
    hdrs = {
        "User-Agent": "RTDL-XHD-Deep-Public-Provenance-Probe/5449",
        "Accept": "*/*",
    }
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, method=method, headers=hdrs)
    started = time.perf_counter()
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            body = resp.read(max_body + 1)
            elapsed = time.perf_counter() - started
            truncated = len(body) > max_body
            if truncated:
                body = body[:max_body]
            return {
                "ok": 200 <= resp.status < 300,
                "status": resp.status,
                "url": resp.geturl(),
                "content_type": resp.headers.get("content-type"),
                "content_length_header": resp.headers.get("content-length"),
                "elapsed_sec": elapsed,
                "body": body,
                "body_truncated": truncated,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        body = exc.read(max_body + 1) if exc.fp is not None else b""
        truncated = len(body) > max_body
        if truncated:
            body = body[:max_body]
        return {
            "ok": False,
            "status": exc.code,
            "url": url,
            "content_type": exc.headers.get("content-type") if exc.headers else None,
            "content_length_header": exc.headers.get("content-length") if exc.headers else None,
            "elapsed_sec": elapsed,
            "body": body,
            "body_truncated": truncated,
            "error": f"HTTPError: {exc.reason}",
        }
    except Exception as exc:  # noqa: BLE001 - evidence should capture failures.
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "status": None,
            "url": url,
            "content_type": None,
            "content_length_header": None,
            "elapsed_sec": elapsed,
            "body": b"",
            "body_truncated": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _public_response(resp: dict[str, Any]) -> dict[str, Any]:
    body = resp["body"]
    return {
        "ok": resp["ok"],
        "status": resp["status"],
        "url": resp["url"],
        "content_type": resp["content_type"],
        "content_length_header": resp["content_length_header"],
        "elapsed_sec": resp["elapsed_sec"],
        "body_bytes": len(body),
        "body_prefix_hex": body[:16].hex(),
        "body_truncated": resp["body_truncated"],
        "zip_magic_observed": body.startswith(b"PK\x03\x04"),
        "error": resp["error"],
    }


def _json_get(url: str, *, timeout: float = 20.0, max_body: int = 5_000_000) -> tuple[dict[str, Any], Any | None]:
    resp = _request(url, timeout=timeout, max_body=max_body)
    public = _public_response(resp)
    body = resp["body"]
    if public["ok"] and body and not public["body_truncated"]:
        try:
            return public, json.loads(body.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            public["json_error"] = f"{type(exc).__name__}: {exc}"
    return public, None


def _artifact_like(value: str) -> bool:
    lower = value.lower()
    return any(term in lower for term in ARTIFACT_TERMS)


def _is_repo_log_path(path: str) -> bool:
    lower = path.lower()
    return lower.startswith(LOG_PREFIXES)


def _is_source_path(path: str) -> bool:
    lower = path.lower()
    return lower.startswith(SOURCE_PREFIXES) or lower.endswith(SOURCE_SUFFIXES)


def _is_data_file_path(path: str) -> bool:
    lower = path.lower()
    return lower.endswith(DATA_FILE_SUFFIXES)


def _is_xhd_relevant_text(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in XHD_RELEVANCE_TERMS)


def _probe_github_metadata() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for key, url in {
        "releases": f"{REPO_API}/releases",
        "tags": f"{REPO_API}/tags",
        "issues": f"{REPO_API}/issues?state=all&per_page=100",
        "pulls": f"{REPO_API}/pulls?state=all&per_page=100",
        "pages": f"{REPO_API}/pages",
    }.items():
        response, payload = _json_get(url, timeout=20.0)
        rows[key] = {"response": response, "payload_sample": _payload_sample(payload)}

    release_assets: list[dict[str, Any]] = []
    releases = rows["releases"]["payload_sample"].get("raw", [])
    if isinstance(releases, list):
        for release in releases:
            for asset in release.get("assets", []):
                release_assets.append(
                    {
                        "release": release.get("tag_name"),
                        "name": asset.get("name"),
                        "url": asset.get("browser_download_url"),
                        "size": asset.get("size"),
                        "artifact_like": _artifact_like(str(asset.get("name", ""))),
                    }
                )

    issue_artifact_mentions = []
    issues = rows["issues"]["payload_sample"].get("raw", [])
    if isinstance(issues, list):
        for issue in issues:
            text = " ".join(str(issue.get(field, "")) for field in ("title", "body", "html_url"))
            if _artifact_like(text):
                issue_artifact_mentions.append(
                    {
                        "number": issue.get("number"),
                        "title": issue.get("title"),
                        "html_url": issue.get("html_url"),
                    }
                )

    return {
        "surfaces": rows,
        "release_asset_count": len(release_assets),
        "artifact_like_release_assets": [row for row in release_assets if row["artifact_like"]],
        "artifact_like_issue_mentions": issue_artifact_mentions[:20],
        "github_metadata_artifact_candidate_found": bool(
            [row for row in release_assets if row["artifact_like"]] or issue_artifact_mentions
        ),
    }


def _payload_sample(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return {
            "type": "list",
            "count": len(payload),
            "raw": payload[:100],
        }
    if isinstance(payload, dict):
        slim = dict(payload)
        for key in list(slim):
            if key in {"tree", "items", "data", "results"} and isinstance(slim[key], list):
                slim[key] = slim[key][:100]
        return {"type": "dict", "raw": slim}
    return {"type": type(payload).__name__, "raw": payload}


def _probe_github_data_paths() -> dict[str, Any]:
    rows = []
    found = []
    for branch in BRANCHES:
        for path in DATA_PATH_CANDIDATES:
            encoded = urllib.parse.quote(path, safe="/")
            url = f"{REPO_API}/contents/{encoded}?ref={urllib.parse.quote(branch)}"
            response, payload = _json_get(url, timeout=15.0, max_body=1_000_000)
            exists = response["ok"]
            row = {
                "branch": branch,
                "path": path,
                "response": response,
                "exists": exists,
                "kind": None,
                "candidate_exact_input": False,
                "reason": "not_found",
            }
            if exists:
                row["reason"] = "path_exists_requires_human_inspection"
                if isinstance(payload, dict):
                    row["kind"] = payload.get("type")
                    row["size"] = payload.get("size")
                    row["download_url"] = payload.get("download_url")
                elif isinstance(payload, list):
                    row["kind"] = "directory"
                    row["child_count"] = len(payload)
                    row["children"] = [
                        {"name": child.get("name"), "type": child.get("type"), "size": child.get("size")}
                        for child in payload[:20]
                    ]
                row["candidate_exact_input"] = True
                found.append(row)
            rows.append(row)
    return {
        "checked_count": len(rows),
        "found_count": len(found),
        "found_paths": found,
        "checks": rows,
    }


def _probe_github_branch_trees() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    exact_candidates: list[dict[str, Any]] = []
    for branch, sha in BRANCHES.items():
        response, payload = _json_get(f"{REPO_API}/git/trees/{sha}?recursive=1", timeout=30.0, max_body=20_000_000)
        tree = payload.get("tree", []) if isinstance(payload, dict) else []
        matches = []
        non_log_candidates = []
        for item in tree:
            path = str(item.get("path", ""))
            if not _artifact_like(path):
                continue
            entry = {
                "path": path,
                "type": item.get("type"),
                "size": item.get("size"),
                "is_log_path": _is_repo_log_path(path),
            }
            matches.append(entry)
            if (
                item.get("type") == "blob"
                and not _is_repo_log_path(path)
                and not _is_source_path(path)
                and _is_data_file_path(path)
            ):
                non_log_candidates.append(entry)
        rows[branch] = {
            "response": response,
            "tree_path_count": len(tree),
            "artifact_like_path_count": len(matches),
            "non_log_artifact_like_blob_count": len(non_log_candidates),
            "artifact_like_paths_sample": matches[:80],
            "non_log_artifact_like_blobs": non_log_candidates[:80],
        }
        exact_candidates.extend({"branch": branch, **row} for row in non_log_candidates)
    return {
        "branches": rows,
        "non_log_artifact_like_blob_count": len(exact_candidates),
        "non_log_artifact_like_blobs": exact_candidates[:120],
        "tree_exact_input_candidate_found": bool(exact_candidates),
    }


def _probe_registries() -> dict[str, Any]:
    rows = {}
    candidates = []
    for name, url in REGISTRY_URLS.items():
        response, payload = _json_get(url, timeout=25.0, max_body=5_000_000)
        text = json.dumps(payload, sort_keys=True)[:200_000].lower() if payload is not None else ""
        artifact_like = _artifact_like(text)
        candidate_records = _registry_candidate_records(name, payload)
        rows[name] = {
            "url": url,
            "response": response,
            "artifact_like_terms_observed": artifact_like,
            "xhd_relevant_artifact_candidate_count": len(candidate_records),
            "xhd_relevant_artifact_candidates": candidate_records[:20],
            "payload_sample": _payload_sample(payload),
        }
        if candidate_records:
            candidates.append(name)
    return {
        "registries": rows,
        "artifact_like_registry_count": len(candidates),
        "artifact_like_registries": candidates,
        "registry_dataset_candidate_found": bool(candidates),
    }


def _registry_candidate_records(name: str, payload: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if name == "crossref_work" and isinstance(payload, dict):
        message = payload.get("message", {})
        links = message.get("link", []) if isinstance(message, dict) else []
        relations = message.get("relation", {}) if isinstance(message, dict) else {}
        for link in links:
            url = str(link.get("URL", ""))
            if _artifact_like(url):
                records.append({"source": name, "kind": "crossref_link", "url": url, "link": link})
        for relation_key, values in relations.items():
            for value in values if isinstance(values, list) else []:
                blob = json.dumps(value, sort_keys=True)
                if _artifact_like(blob):
                    records.append({"source": name, "kind": f"crossref_relation:{relation_key}", "value": value})
        return records

    if name == "datacite_query" and isinstance(payload, dict):
        for row in payload.get("data", [])[:100]:
            blob = json.dumps(row, sort_keys=True)
            if _is_xhd_relevant_text(blob) and _artifact_like(blob):
                records.append({"source": name, "kind": "datacite_result", "id": row.get("id")})
        return records

    if name == "zenodo_query" and isinstance(payload, dict):
        hits = payload.get("hits", {}).get("hits", [])
        for row in hits[:100]:
            metadata = row.get("metadata", {})
            title = str(metadata.get("title", row.get("title", "")))
            description = str(metadata.get("description", ""))
            repo = json.dumps(metadata.get("custom", {}), sort_keys=True)
            identifiers = json.dumps(metadata.get("related_identifiers", []), sort_keys=True)
            relevant_text = " ".join([title, description, repo, identifiers, str(row.get("doi", ""))])
            if _is_xhd_relevant_text(relevant_text):
                files = [
                    {"key": file.get("key"), "size": file.get("size"), "checksum": file.get("checksum")}
                    for file in row.get("files", [])
                    if _artifact_like(str(file.get("key", "")))
                ]
                records.append(
                    {
                        "source": name,
                        "kind": "zenodo_result",
                        "id": row.get("id"),
                        "title": title,
                        "doi": row.get("doi"),
                        "artifact_like_files": files,
                    }
                )
        return records

    if name == "openalex_work" and isinstance(payload, dict):
        urls = []
        for key in ("best_oa_location", "primary_location"):
            location = payload.get(key)
            if isinstance(location, dict):
                for url_key in ("landing_page_url", "pdf_url"):
                    if location.get(url_key):
                        urls.append(str(location[url_key]))
        for location in payload.get("locations", []) if isinstance(payload.get("locations"), list) else []:
            if isinstance(location, dict):
                for url_key in ("landing_page_url", "pdf_url"):
                    if location.get(url_key):
                        urls.append(str(location[url_key]))
        for url in urls:
            if _artifact_like(url) and _is_xhd_relevant_text(url):
                records.append({"source": name, "kind": "openalex_location", "url": url})
        return records

    return records


def _probe_acm_variants() -> dict[str, Any]:
    rows = []
    zip_successes = []
    for url in ACM_URL_VARIANTS:
        response = _public_response(_request(url, headers={"Range": "bytes=0-3"}, timeout=20.0, max_body=4096))
        row = {"url": url, "range_get": response}
        if response["ok"] and response["zip_magic_observed"]:
            zip_successes.append(row)
        rows.append(row)
    return {
        "variant_count": len(rows),
        "zip_success_count": len(zip_successes),
        "zip_successes": zip_successes,
        "checks": rows,
        "acm_direct_download_success": bool(zip_successes),
    }


def build_payload() -> dict[str, Any]:
    github_metadata = _probe_github_metadata()
    github_data_paths = _probe_github_data_paths()
    github_branch_trees = _probe_github_branch_trees()
    registries = _probe_registries()
    acm_variants = _probe_acm_variants()

    candidate_found = bool(
        github_metadata["github_metadata_artifact_candidate_found"]
        or github_data_paths["found_count"]
        or github_branch_trees["tree_exact_input_candidate_found"]
        or registries["registry_dataset_candidate_found"]
        or acm_variants["acm_direct_download_success"]
    )
    status = (
        "deep_public_mirror_probe_possible_public_artifact_requires_human_inspection"
        if candidate_found
        else "deep_public_mirror_probe_no_new_exact_input_path__external_event_still_required"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5449.deep_public_mirror_probe.v1",
        "goal": "Goal5449",
        "date": "2026-07-10",
        "purpose": (
            "Probe public mirror and registry surfaces beyond Goal5442 without using POD or route work as a "
            "substitute for missing exact input artifacts."
        ),
        "status": status,
        "source_context": {
            "extends": [
                "Goal5442 public provenance rescan",
                "Goal5448 external path readiness audit",
            ],
            "not_repeated_as_primary_surfaces": [
                "standard GitHub release/root/tree main summary already embedded by Goal5432",
                "shallow Crossref link list already embedded by Goal5432",
                "ACM known supplement URLs already probed by Goal5443",
            ],
        },
        "deep_surfaces": {
            "github_metadata": github_metadata,
            "github_data_paths": github_data_paths,
            "github_branch_trees": github_branch_trees,
            "registries": registries,
            "acm_url_variants": acm_variants,
        },
        "classification": {
            "github_issue_or_release_artifact_found": github_metadata["github_metadata_artifact_candidate_found"],
            "github_raw_or_contents_data_path_found": bool(github_data_paths["found_count"]),
            "github_non_log_tree_artifact_blob_found": github_branch_trees["tree_exact_input_candidate_found"],
            "registry_dataset_candidate_found": registries["registry_dataset_candidate_found"],
            "acm_direct_download_success": acm_variants["acm_direct_download_success"],
            "new_public_exact_input_artifact_found": candidate_found,
            "exact_input_blocker_removed": False,
            "pod_expected_next": False,
        },
        "interpretation": {
            "if_candidate_found": (
                "Candidate public artifact still requires human inspection / hash mapping before any exact-input claim."
            ),
            "if_no_candidate_found": (
                "The deeper public mirror surfaces checked by this goal did not reveal exact input bytes or hashes. "
                "The next movement remains a real external event: sent request, author/ACM response, authorized "
                "supplement zip, author archive, or accepted exact-equivalence verdict."
            ),
            "pod_expected_next": False,
            "reason_pod_not_expected": (
                "POD cannot create missing public provenance. It is useful only after exact artifacts, hashes, "
                "byte-identical regeneration, inspectable supplement contents, or accepted exact-equivalence evidence appears."
            ),
        },
        "claim_boundary": {
            "deep_public_mirror_probe_claimed": True,
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
            "gate_non_app_consumer": "deep public mirror/provenance probe / exact-input governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: external provenance evidence, not app-artifact parity implementation.",
        },
        "allowed_summary": (
            "Goal5449 probes deeper public mirror and registry surfaces beyond Goal5442. It either records "
            "inspectable public candidates or confirms that no new exact-input public path was found on those surfaces."
        ),
        "not_allowed": [
            "claiming exact input recovery from a candidate without byte/hash inspection",
            "claiming GitHub logs or paper metadata are input artifacts",
            "claiming ACM supplement contents were inspected unless zip bytes are available",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD, route tuning, explicit -lb, or app-artifact parity work as a substitute for missing provenance",
        ],
        "exit_label": status,
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "new_public_exact_input_artifact_found": payload["classification"][
                    "new_public_exact_input_artifact_found"
                ],
                "exact_input_blocker_removed": payload["classification"]["exact_input_blocker_removed"],
                "pod_expected_next": payload["classification"]["pod_expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
