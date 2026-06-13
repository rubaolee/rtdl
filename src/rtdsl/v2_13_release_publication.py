from __future__ import annotations

import json
from pathlib import Path
from typing import Any


V2_13_RELEASE_PUBLICATION_VERSION = "rtdl.v2_13.release_publication.goal4371.v1"

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLIC_WORDING = ROOT / "docs" / "reports" / "goal4370_v2_13_public_wording_packet_2026-06-13.json"
DEFAULT_HUMAN_SCALE = ROOT / "docs" / "reports" / "goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.json"
DEFAULT_EMBREE_FAIRNESS = ROOT / "docs" / "reports" / "goal4369_embree_cpu_fairness_hardening_2026-06-13.json"
DEFAULT_RAYJOIN_AUTHORS = ROOT / "docs" / "reports" / "goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.json"
DEFAULT_PIP_EXACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4368_pip_exact_prepared_points_executor_2026-06-13"
    / "summary.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _fmt(value: Any, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}".rstrip("0").rstrip(".")


def _human_row(rows: list[dict[str, Any]], app: str) -> dict[str, Any]:
    return next(row for row in rows if row["app"] == app)


def _public_row(rows: list[dict[str, Any]], app: str) -> dict[str, Any]:
    return next(row for row in rows if row["app"] == app)


def _promoted_app_id(app: str) -> str:
    if app in {"spatial_rayjoin_lsi", "spatial_rayjoin_pip"}:
        return "spatial_rayjoin"
    return app


def v2_13_release_publication_packet(
    *,
    public_wording_path: Path | None = None,
    human_scale_path: Path | None = None,
    embree_fairness_path: Path | None = None,
    rayjoin_authors_path: Path | None = None,
    pip_exact_path: Path | None = None,
) -> dict[str, Any]:
    public_path = public_wording_path or DEFAULT_PUBLIC_WORDING
    human_path = human_scale_path or DEFAULT_HUMAN_SCALE
    fairness_path = embree_fairness_path or DEFAULT_EMBREE_FAIRNESS
    rayjoin_path = rayjoin_authors_path or DEFAULT_RAYJOIN_AUTHORS
    pip_path = pip_exact_path or DEFAULT_PIP_EXACT

    public = _load_json(public_path)
    human = _load_json(human_path)
    fairness = _load_json(fairness_path)
    rayjoin = _load_json(rayjoin_path)
    pip = _load_json(pip_path)

    public_rows = list(public["rows"])
    human_rows = list(human["rows"])
    promoted_app_count = len({_promoted_app_id(row["app"]) for row in public_rows})
    pip_public = _public_row(public_rows, "spatial_rayjoin_pip")
    lsi_public = _public_row(public_rows, "spatial_rayjoin_lsi")
    rtnn_public = _public_row(public_rows, "rtnn")

    pip_optix = pip["rtdl"]["pip"]["backends"]["optix"]
    pip_embree = pip["rtdl"]["pip"]["backends"]["embree"]
    pip_exact_ratio = float(pip_embree["hot_median_sec"]) / float(pip_optix["hot_median_sec"])
    pip_rayjoin_rt_ratio = next(
        float(row["rayjoin_rt_over_rtdl"])
        for row in pip["comparisons"]
        if row["backend"] == "optix"
    )

    errors: list[str] = []
    for label, payload in (
        ("public wording", public),
        ("human-scale", human),
        ("Embree fairness", fairness),
        ("RayJoin authors-code", rayjoin),
    ):
        if payload.get("validation", {}).get("status") != "accept":
            errors.append(f"{label} packet is not accepted")
    if not pip.get("rtdl", {}).get("pip", {}).get("correctness", {}).get("cross_backend_counts_match"):
        errors.append("Goal4368 PIP exact packet does not record cross-backend count agreement")
    if len(public_rows) != 11 or len(human_rows) != 11:
        errors.append("v2.13 release table must cover eleven scoped rows")
    if promoted_app_count != 10:
        errors.append("v2.13 release table must cover ten promoted benchmark apps")
    if public["summary"].get("row_scoped_public_wording_authorized_count") != 10:
        errors.append("public wording must authorize exactly ten row-scoped rows")
    if public["summary"].get("blocked_row_count") != 1:
        errors.append("public wording must block exactly one row")
    if public["summary"].get("zero_unexplained_rows") is not True:
        errors.append("public wording must have zero unexplained rows")
    if rtnn_public["public_wording_status"] != "blocked_not_rt_core_neighbor_search_claim":
        errors.append("RTNN must remain blocked as an RT-core neighbor-search claim")
    if pip_public["public_wording_status"] != "ready_row_scoped_embree_faster_wording":
        errors.append("human-scale PIP row must be published as near-parity/Embree-faster wording")
    if float(pip_public["speedup_embree_per_iter_div_optix_per_iter"]) >= 1.0:
        errors.append("human-scale PIP row should not be worded as an OptiX speedup")
    if pip_exact_ratio <= 3.0:
        errors.append("Goal4368 exact same-stream PIP OptiX/Embree ratio should stay above 3x")
    if pip_rayjoin_rt_ratio >= 1.0:
        errors.append("Goal4368 PIP must not imply RTDL beats RayJoin RT")
    if fairness["summary"].get("fallback_detected_row_count") != 0:
        errors.append("Embree fairness packet must have zero fallback rows")
    if fairness["summary"].get("embree_rt_core_accelerated_row_count") != 0:
        errors.append("Embree CPU rows must not be marked RT-core accelerated")
    if fairness["summary"].get("fresh_threaded_cpu_reference_threads") != 8:
        errors.append("fresh Embree CPU reference must record threads=8")
    for row in human_rows:
        if not (1.0 <= float(row["optix_total_sec"]) <= 10.0):
            errors.append(f"{row['app']} OptiX aggregate is outside 1-10s")
        if not (1.0 <= float(row["embree_total_sec"]) <= 10.0):
            errors.append(f"{row['app']} Embree aggregate is outside 1-10s")

    blocked_wording = tuple(public["blocked_wording"])
    return {
        "version": V2_13_RELEASE_PUBLICATION_VERSION,
        "status": "published_source_tree_release_package" if not errors else "reject",
        "release": {
            "version_marker": "v2.13",
            "pyproject_version": "2.13.0",
            "release_date": "2026-06-13",
            "release_dir": "docs/release_reports/v2_13",
        },
        "source_artifacts": {
            "public_wording": _relative(public_path),
            "human_scale": _relative(human_path),
            "embree_fairness": _relative(fairness_path),
            "rayjoin_authors_code": _relative(rayjoin_path),
            "pip_exact": _relative(pip_path),
        },
        "summary": {
            "promoted_app_count": promoted_app_count,
            "scoped_row_count": len(public_rows),
            "row_scoped_wording_authorized_count": public["summary"]["row_scoped_public_wording_authorized_count"],
            "blocked_row_count": public["summary"]["blocked_row_count"],
            "human_scale_all_rows_in_1_to_10_sec_band": not any(
                not (1.0 <= float(row["optix_total_sec"]) <= 10.0)
                or not (1.0 <= float(row["embree_total_sec"]) <= 10.0)
                for row in human_rows
            ),
            "human_scale_pip_embree_divided_by_optix": round(
                float(pip_public["speedup_embree_per_iter_div_optix_per_iter"]), 3
            ),
            "goal4368_exact_pip_embree_divided_by_optix": round(pip_exact_ratio, 3),
            "goal4368_rayjoin_rt_faster_than_rtdl_optix_pip": round(1.0 / pip_rayjoin_rt_ratio, 2),
            "rayjoin_lsi_human_scale_embree_divided_by_optix": round(
                float(lsi_public["speedup_embree_per_iter_div_optix_per_iter"]), 3
            ),
            "broad_rt_core_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "rayjoin_whole_system_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "intel_gpu_performance_claim_authorized": False,
            "amd_gpu_performance_claim_authorized": False,
            "prepare_amd_gpu_now": False,
            "prepare_amd_gpu_after_v2_13_close": True,
        },
        "rows": public_rows,
        "release_statement": (
            "RTDL v2.13 is the current source-tree release for the refreshed row-scoped "
            "NVIDIA OptiX/RT-core versus Embree CPU comparison. The release keeps every "
            "published performance sentence tied to a benchmark row, contract, direction, "
            "and caveat."
        ),
        "pip_interpretation": (
            "PIP is deliberately mixed: the refreshed human-scale public CDB slice is "
            "near parity and slightly Embree-faster, while Goal4368 shows the stricter "
            "full same-stream exact prepared-points executor is 3.22x faster on OptiX "
            "than Embree and still 7.28x slower than RayJoin RT. Do not collapse those "
            "facts into a broad RT-core or RTDL-beats-RayJoin claim."
        ),
        "allowed_public_wording": public["allowed_portfolio_wording"],
        "blocked_wording": blocked_wording,
        "validation": {"status": "accept" if not errors else "reject", "errors": errors},
    }


def markdown_v2_13_public_rt_vs_embree_comparison(payload: dict[str, Any]) -> str:
    lines = [
        "# RTDL v2.13 Row-Scoped RT-Core vs Embree CPU Comparison",
        "",
        "Status: release-facing row-scoped comparison; not broad speedup wording.",
        "",
        "| App | Status | Directional readout | Contract | Allowed wording |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        ratio = float(row["speedup_embree_per_iter_div_optix_per_iter"])
        if ratio >= 1.0:
            readout = f"OptiX {ratio:.2f}x faster"
        else:
            readout = f"Embree {1.0 / ratio:.2f}x faster"
        lines.append(
            "| {app} | `{status}` | {readout} | `{contract}` | {wording} |".format(
                app=row["app"],
                status=row["public_wording_status"],
                readout=readout,
                contract=row["contract"],
                wording=row["allowed_wording"],
            )
        )
    lines.extend(
        [
            "",
            "## PIP Reading",
            "",
            payload["pip_interpretation"],
            "",
            "## Blocked Wording",
            "",
        ]
    )
    for item in payload["blocked_wording"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Validation status: `{payload['validation']['status']}`."])
    return "\n".join(lines) + "\n"


def markdown_v2_13_release_readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# RTDL v2.13 Release Package",
        "",
        "Status: published source-tree release package.",
        "",
        "Version marker: `v2.13`",
        "",
        "Release date: 2026-06-13",
        "",
        "## Release Statement",
        "",
        payload["release_statement"],
        "",
        "Use RTDL directly from a checkout:",
        "",
        "```bash",
        "PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py",
        "```",
        "",
        "This is not a package-install release, not automatic partner selection, "
        "not whole-application speedup wording, not RTDL-beats-RayJoin wording, "
        "not RayJoin paper reproduction, and not Intel/AMD GPU performance wording.",
        "",
        "## Comparison Summary",
        "",
        "Read the detailed table in [v2.13 row-scoped RT-core vs Embree CPU comparison](public_rt_vs_embree_comparison.md).",
        "",
        "| Result bucket | Count / value |",
        "| --- | ---: |",
        f"| Promoted apps covered | {summary['promoted_app_count']} |",
        f"| Scoped comparison rows | {summary['scoped_row_count']} |",
        f"| Row-scoped wording-authorized rows | {summary['row_scoped_wording_authorized_count']} |",
        f"| Blocked rows | {summary['blocked_row_count']} |",
        f"| Human-scale rows in 1-10s band | {summary['human_scale_all_rows_in_1_to_10_sec_band']} |",
        f"| Human-scale PIP Embree/OptiX | {summary['human_scale_pip_embree_divided_by_optix']}x |",
        f"| Goal4368 exact PIP Embree/OptiX | {summary['goal4368_exact_pip_embree_divided_by_optix']}x |",
        "",
        "## Important Mixed Rows",
        "",
        "- Spatial RayJoin PIP is near parity and slightly Embree-faster in the refreshed human-scale public CDB slice.",
        "- Goal4368 separately records the full same-stream exact PIP executor: OptiX is faster than Embree there, but RayJoin RT is still faster than RTDL PIP.",
        "- RTNN remains blocked as an RT-core neighbor-search claim.",
        "- RT-DBSCAN uses RTDL plus the same fixed Numba continuation policy.",
        "",
        "## Evidence",
        "",
        "- [v2.13 publication note](publication.md)",
        "- [v2.13 tag preparation](tag_preparation.md)",
        "- [v2.13 row-scoped comparison](public_rt_vs_embree_comparison.md)",
        "- [Goal4370 public wording packet](../../reports/goal4370_v2_13_public_wording_packet_2026-06-13.md)",
        "- [Goal4349 refreshed human-scale packet](../../reports/goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.md)",
        "- [Goal4369 Embree CPU fairness packet](../../reports/goal4369_embree_cpu_fairness_hardening_2026-06-13.md)",
        "- [Goal4368 PIP exact prepared-points executor](../../reports/goal4368_pip_exact_prepared_points_executor_2026-06-13.md)",
        "- [Goal4367 RayJoin authors-code packet](../../reports/goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.md)",
        "",
        "## Release Boundary",
        "",
        "RTDL v2.13 authorizes the source-tree marker and the row-scoped wording above. "
        "It does not authorize broad RT-core speedup, whole-application speedup, "
        "package-install, automatic partner selection, RTDL-beats-RayJoin, RayJoin paper "
        "reproduction, Intel GPU performance, AMD GPU performance, or general zero-copy/device-residency claims.",
        "",
        f"Validation status: `{payload['validation']['status']}`.",
    ]
    return "\n".join(lines) + "\n"


def markdown_v2_13_publication(payload: dict[str, Any]) -> str:
    lines = [
        "# RTDL v2.13 Publication Note",
        "",
        "Status: published source-tree publication packet.",
        "",
        "Date: 2026-06-13",
        "",
        "Version marker: `v2.13`",
        "",
        "## Published Statement",
        "",
        payload["release_statement"],
        "",
        "## Public Wording That Is Allowed",
        "",
        "```text",
        payload["allowed_public_wording"],
        "```",
        "",
        "PIP wording must include the mixed-row distinction:",
        "",
        "```text",
        "Spatial RayJoin PIP is not a broad RT-core win in v2.13. The refreshed human-scale public CDB slice is near parity and slightly Embree-faster; the stricter Goal4368 full same-stream exact executor is an OptiX-over-Embree engineering win but still slower than RayJoin RT.",
        "```",
        "",
        "## Public Wording That Is Blocked",
        "",
    ]
    for item in payload["blocked_wording"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Validation Summary",
            "",
            "- Refreshed human-scale packet: pass with all rows in the 1-10s aggregate band.",
            "- Embree CPU fairness packet: pass with threads=8 reference, zero fallbacks, and zero RT-core-accelerated Embree rows.",
            "- Public wording packet: pass with zero unexplained rows.",
            "- Goal4368 PIP exact executor: pass; exact counts match and RayJoin RT remains faster than RTDL PIP.",
            "",
            "## Publication Boundary",
            "",
            "This publication packet authorizes bounded row-scoped wording only.",
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def markdown_v2_13_tag_preparation(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# RTDL v2.13 Tag Preparation",
            "",
            "Status: ready after publication commit.",
            "",
            "Intended tag: `v2.13`",
            "",
            "## Required Commit Contents",
            "",
            "- `VERSION` set to `v2.13`.",
            "- `pyproject.toml` project version set to `2.13.0`.",
            "- `docs/release_reports/v2_13/README.md`.",
            "- `docs/release_reports/v2_13/publication.md`.",
            "- `docs/release_reports/v2_13/tag_preparation.md`.",
            "- `docs/release_reports/v2_13/public_rt_vs_embree_comparison.md` and `.json`.",
            "- Refreshed Goal4349, Goal4368, Goal4369, and Goal4370 evidence artifacts.",
            "",
            "## Required Validation",
            "",
            "```bash",
            "PYTHONPATH=src:. python -m unittest \\",
            "  tests.goal4349_human_scale_rt_vs_embree_comparison_test \\",
            "  tests.goal4368_pip_exact_prepared_points_executor_test \\",
            "  tests.goal4369_embree_cpu_fairness_packet_test \\",
            "  tests.goal4370_v2_13_public_wording_packet_test \\",
            "  tests.goal4371_v2_13_release_publication_test",
            "```",
            "",
            "On the NVIDIA pod, run the same focused tests with the native library environment configured.",
            "",
            "## Tag Command",
            "",
            "```bash",
            "git tag -a v2.13 -m \"RTDL v2.13 source-tree release\"",
            "```",
            "",
            "Do not move a published `v2.13` tag without explicit maintainer decision.",
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    ) + "\n"
