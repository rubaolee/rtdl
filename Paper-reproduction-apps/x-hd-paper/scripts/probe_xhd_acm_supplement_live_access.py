#!/usr/bin/env python3
"""Probe live access to the X-HD ACM supplementary zip.

This app-owned helper is intentionally narrow: it checks whether the known ACM
supplement URLs are downloadable from the current environment, optionally using
an explicit cookie header, and records enough evidence for the existing
Goal5335-Goal5340 local provenance chain to continue.

It does not inspect the zip contents, claim exact paper input identity, run POD,
or compare author/RTDL outputs.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Tuple


DEFAULT_URLS = [
    "https://dl.acm.org/action/downloadSupplement?doi=10.1145%2F3797905.3800509&file=ics26-106.zip",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip",
    "https://dl.acm.org/doi/suppl/10.1145/3797905.3800509/suppl_file/ics26-106.zip?download=true",
]


def _load_cookie_header(path: pathlib.Path | None) -> str | None:
    if path is None:
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"cookie file is empty: {path}")
    if "\n" in text:
        raise ValueError("cookie file must contain a single Cookie header value")
    return text


def _request(
    url: str,
    *,
    method: str,
    timeout_sec: float,
    cookie_header: str | None,
    range_header: str | None = None,
) -> Tuple[Dict[str, Any], bytes]:
    headers = {
        "User-Agent": "rtdl-xhd-provenance-probe/1.0",
        "Accept": "*/*",
    }
    if cookie_header:
        headers["Cookie"] = cookie_header
    if range_header:
        headers["Range"] = range_header
    req = urllib.request.Request(url, headers=headers, method=method)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read(4096)
            elapsed = time.time() - started
            headers_dict = {k.lower(): v for k, v in resp.headers.items()}
            return (
                {
                    "url": url,
                    "method": method,
                    "ok": 200 <= int(resp.status) < 400,
                    "status": int(resp.status),
                    "content_type": headers_dict.get("content-type"),
                    "content_length": headers_dict.get("content-length"),
                    "content_range": headers_dict.get("content-range"),
                    "elapsed_sec": elapsed,
                    "error": None,
                },
                body,
            )
    except urllib.error.HTTPError as exc:
        elapsed = time.time() - started
        body = exc.read(4096)
        headers_dict = {k.lower(): v for k, v in exc.headers.items()}
        return (
            {
                "url": url,
                "method": method,
                "ok": False,
                "status": int(exc.code),
                "content_type": headers_dict.get("content-type"),
                "content_length": headers_dict.get("content-length"),
                "content_range": headers_dict.get("content-range"),
                "elapsed_sec": elapsed,
                "error": f"HTTPError: {exc.code}",
            },
            body,
        )
    except Exception as exc:
        elapsed = time.time() - started
        return (
            {
                "url": url,
                "method": method,
                "ok": False,
                "status": None,
                "content_type": None,
                "content_length": None,
                "content_range": None,
                "elapsed_sec": elapsed,
                "error": f"{type(exc).__name__}: {exc}",
            },
            b"",
        )


def _body_fingerprint(body: bytes) -> Dict[str, Any]:
    sample = body[:16]
    return {
        "sample_len": len(body),
        "sample_hex": sample.hex(),
        "zip_magic": body.startswith(b"PK\x03\x04") or body.startswith(b"PK\x05\x06") or body.startswith(b"PK\x07\x08"),
    }


def _classify(url_checks: Iterable[Dict[str, Any]]) -> str:
    checks = list(url_checks)
    if any(check.get("range_get", {}).get("zip_magic") for check in checks):
        return "acm_supplement_zip_magic_observed__ready_for_download_or_inspection"
    if any(check.get("head", {}).get("status") == 403 or check.get("range_get", {}).get("status") == 403 for check in checks):
        return "acm_supplement_visible_but_forbidden_from_current_environment"
    if any(check.get("head", {}).get("ok") or check.get("range_get", {}).get("ok") for check in checks):
        return "acm_supplement_reachable_but_zip_magic_not_observed"
    return "acm_supplement_not_downloadable_from_current_environment"


def build_probe(
    *,
    urls: List[str],
    timeout_sec: float,
    cookie_header: str | None,
    do_range_get: bool,
) -> Dict[str, Any]:
    url_checks: List[Dict[str, Any]] = []
    for url in urls:
        head, _ = _request(url, method="HEAD", timeout_sec=timeout_sec, cookie_header=cookie_header)
        range_meta: Dict[str, Any]
        if do_range_get:
            range_response, body = _request(
                url,
                method="GET",
                timeout_sec=timeout_sec,
                cookie_header=cookie_header,
                range_header="bytes=0-15",
            )
            range_meta = {**range_response, **_body_fingerprint(body)}
        else:
            range_meta = {"skipped": True, "zip_magic": False}
        url_checks.append({"url": url, "head": head, "range_get": range_meta})

    classification = _classify(url_checks)
    return {
        "schema": "rtdl.paper_reproduction.xhd.acm_supplement_live_access_probe.v1",
        "doi": "10.1145/3797905.3800509",
        "artifact_name": "ics26-106.zip",
        "urls": urls,
        "used_cookie_header": bool(cookie_header),
        "classification": classification,
        "url_checks": url_checks,
        "next_action": _next_action(classification),
        "claim_boundary": {
            "acm_supplement_inspected": False,
            "zip_contents_inspected": False,
            "candidate_workload_mapping_accepted": False,
            "same_input_gate_passed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Live access/provenance probe only. POD is useful only after inspected artifacts, accepted workload mapping, and command packet readiness.",
        },
    }


def _next_action(classification: str) -> str:
    if classification == "acm_supplement_zip_magic_observed__ready_for_download_or_inspection":
        return "download with authorized access, then run inspect_xhd_acm_supplement_zip.py and the Goal5336-Goal5340 local chain"
    if classification == "acm_supplement_visible_but_forbidden_from_current_environment":
        return "obtain ACM-authorized access/cookie or author artifact; do not infer contents from forbidden response"
    if classification == "acm_supplement_reachable_but_zip_magic_not_observed":
        return "inspect response manually; do not treat as X-HD input artifact until zip contents are verified"
    return "continue external artifact request/intake path; no POD"


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", default=None, help="Override or add supplement URL; repeatable.")
    parser.add_argument("--cookie-file", type=pathlib.Path, default=None)
    parser.add_argument("--timeout-sec", type=float, default=20.0)
    parser.add_argument("--no-range-get", action="store_true")
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    urls = args.url or DEFAULT_URLS
    try:
        cookie_header = _load_cookie_header(args.cookie_file)
        probe = build_probe(
            urls=urls,
            timeout_sec=args.timeout_sec,
            cookie_header=cookie_header,
            do_range_get=not args.no_range_get,
        )
    except Exception as exc:
        print(f"ACM supplement live access probe failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(probe, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
