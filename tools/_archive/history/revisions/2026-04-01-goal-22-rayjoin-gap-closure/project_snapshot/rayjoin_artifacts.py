from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .datasets import rayjoin_bounded_plans
from .datasets import rayjoin_public_assets
from .paper_reproduction import dataset_families
from .paper_reproduction import local_profiles
from .paper_reproduction import paper_targets


def build_registry_payload() -> dict[str, object]:
    return {
        "paper_targets": [asdict(target) for target in paper_targets()],
        "dataset_families": [asdict(family) for family in dataset_families()],
        "local_profiles": [asdict(profile) for profile in local_profiles()],
        "public_assets": [asdict(asset) for asset in rayjoin_public_assets()],
        "bounded_plans": [asdict(plan) for plan in rayjoin_bounded_plans()],
    }


def generate_goal22_artifacts(output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    registry_payload = build_registry_payload()
    registry_path = output_root / "goal22_reproduction_registry.json"
    registry_path.write_text(json.dumps(registry_payload, indent=2, sort_keys=True), encoding="utf-8")

    table3_path = output_root / "table3_analogue.md"
    table4_path = output_root / "table4_overlay_analogue.md"
    figure15_path = output_root / "figure15_overlay_speedup_analogue.md"
    sources_path = output_root / "dataset_sources.md"
    bounded_path = output_root / "dataset_bounded_preparation.md"

    table3_path.write_text(_render_table3_markdown(), encoding="utf-8")
    table4_path.write_text(_render_table4_markdown(), encoding="utf-8")
    figure15_path.write_text(_render_figure15_markdown(), encoding="utf-8")
    sources_path.write_text(_render_sources_markdown(), encoding="utf-8")
    bounded_path.write_text(_render_bounded_markdown(), encoding="utf-8")

    return {
        "registry": registry_path,
        "table3": table3_path,
        "table4": table4_path,
        "figure15": figure15_path,
        "sources": sources_path,
        "bounded": bounded_path,
    }


def _render_table3_markdown() -> str:
    lines = [
        "# Goal 22 Table 3 Analogue",
        "",
        "This table records the current RTDL-on-Embree status for the RayJoin Table 3 targets.",
        "",
        "| Paper Pair | Workload | Dataset Handle | Dataset Status | Preferred Provenance | Local Profile | Current State |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    profile = local_profiles(artifact="table3")[0]
    family_by_handle = {family.handle: family for family in dataset_families()}
    for target in paper_targets(artifact="table3"):
        family = family_by_handle[target.dataset_handle]
        lines.append(
            f"| {target.paper_label} | `{target.workload}` | `{target.dataset_handle}` | "
            f"`{family.current_status}` | `{family.preferred_provenance}` | `{profile.profile_id}` | "
            f"{family.local_plan} |"
        )
    lines.append("")
    lines.append(f"Local profile policy: `{profile.target_runtime}`.")
    return "\n".join(lines).rstrip() + "\n"


def _render_table4_markdown() -> str:
    profile = local_profiles(artifact="table4")[0]
    target = paper_targets(artifact="table4")[0]
    lines = [
        "# Goal 22 Table 4 Overlay Analogue",
        "",
        "This table records the current RTDL-on-Embree status for the RayJoin Table 4 overlay target.",
        "",
        "| Artifact | Workload | Dataset Handle | Fidelity | Current Status | Boundary Note | Local Profile |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        f"| {target.paper_label} | `{target.workload}` | `{target.dataset_handle}` | "
        f"`{profile.fidelity}` | `{target.status}` | `overlay-seed analogue, not full overlay materialization` | "
        f"`{profile.profile_id}` |",
        "",
        f"Local profile policy: `{profile.target_runtime}`.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_figure15_markdown() -> str:
    profile = local_profiles(artifact="figure15")[0]
    target = paper_targets(artifact="figure15")[0]
    lines = [
        "# Goal 22 Figure 15 Overlay Speedup Analogue",
        "",
        "This artifact defines the current reporting contract for the Figure 15 analogue.",
        "",
        "| Artifact | Workload | Input Source | Fidelity | Current Status | Required Label | Local Profile |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        f"| {target.paper_label} | `{target.workload}` | `derived from Table 4 analogue outputs` | "
        f"`{profile.fidelity}` | `{target.status}` | `overlay-seed analogue` | `{profile.profile_id}` |",
        "",
        "Current note:",
        "",
        "- Goal 22 provides the reporting path and metadata boundary.",
        "- Goal 23 will populate this with bounded local run results after the required dataset and table inputs exist.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_sources_markdown() -> str:
    lines = [
        "# Goal 22 Dataset Sources",
        "",
        "This artifact records the current public-source acquisition picture for the missing RayJoin paper dataset families.",
        "",
        "| Asset | Source Type | Current Status | Preferred Use | Source URL | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for asset in rayjoin_public_assets():
        lines.append(
            f"| `{asset.asset_id}` | `{asset.source_type}` | `{asset.current_status}` | "
            f"{asset.preferred_use} | {asset.source_url} | {asset.notes} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_bounded_markdown() -> str:
    lines = [
        "# Goal 22 Bounded Dataset Preparation",
        "",
        "This artifact records the deterministic bounded-local preparation policy for the missing RayJoin paper dataset families.",
        "",
        "| Handle | Current Status | Source Requirement | Runtime Target | Deterministic Rule | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for plan in rayjoin_bounded_plans():
        lines.append(
            f"| `{plan.handle}` | `{plan.current_status}` | {plan.source_requirement} | "
            f"{plan.bounded_runtime_target} | {plan.deterministic_rule} | {plan.notes} |"
        )
    return "\n".join(lines).rstrip() + "\n"
