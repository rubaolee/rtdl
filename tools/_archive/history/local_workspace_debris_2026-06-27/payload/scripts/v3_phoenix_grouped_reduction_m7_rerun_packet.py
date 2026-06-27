#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json"
DEFAULT_MD_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md"

REMOTE_PYTHON = "/root/rtdl_v3_rebuild_20260620/.venv/bin/python"
REMOTE_ART = "/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620"
REMOTE_WORKDIR = "/root/rtdl_v3_rebuild_20260620/current"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Phoenix V3 grouped-reduction M7 rerun packet.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0


def build_payload() -> dict[str, Any]:
    commands = _commands()
    return {
        "version": "phoenix_v3_grouped_reduction_m7_rerun_packet_2026_06_20",
        "status": "ready_for_external_review_not_executed",
        "goal": "Fresh M7-designated grouped_reduction prepared-query rerun",
        "generic_capability": "grouped_reduction",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized_before_run": False,
        "source_feasibility_packet": "docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md",
        "remote": {
            "ssh": "ssh root@213.173.108.14 -p 11592 -i C:\\Users\\Lestat\\.ssh\\id_ed25519_rtdl_codex_current_pod",
            "workdir": REMOTE_WORKDIR,
            "artifact_dir": REMOTE_ART,
            "python": REMOTE_PYTHON,
        },
        "prepared_query_public_contract": {
            "status": "draft_required_before_public_wording",
            "rules": (
                "A prepared-query row must show cold/setup time, hot prepared-query time, and repeat-aware totals together.",
                "Any speedup claim must name the repeat count or say hot prepared-query only.",
                "Single-query end-to-end speedup must be shown even when the intended workload is repeated.",
                "Whole-database or paper-reproduction wording remains false unless a separate packet authorizes it.",
                "Warmup count, repeats, backend, groups, rows, and hardware must be identical or explicitly explained.",
            ),
        },
        "planned_rows": (
            {
                "id": "m7_grouped_reduction_262144",
                "generated_rows": 262144,
                "generated_groups": 1024,
                "modes": ("count", "sum"),
                "backends": ("embree", "optix"),
                "warmup": 3,
                "output": f"{REMOTE_ART}/m7_grouped_reduction_262144_warmup3.json",
            },
            {
                "id": "m7_grouped_reduction_524288",
                "generated_rows": 524288,
                "generated_groups": 2048,
                "modes": ("count", "sum"),
                "backends": ("embree", "optix"),
                "warmup": 3,
                "output": f"{REMOTE_ART}/m7_grouped_reduction_524288_warmup3.json",
            },
        ),
        "required_commands": commands,
        "acceptance_checks": (
            "The packet claim-boundary gate passes on the pod before measurement.",
            "OptiX hardware gate passes before measurement.",
            "Native Embree and OptiX libraries build in the measured source tree.",
            "Both planned scales run with warmup=3 and include independent Embree/OptiX count/sum rows.",
            "Every row records cold_prepare_total_sec, workload_build_sec, elapsed_median_sec, repeat, and warmup.",
            "Every row matches CPU reference and keeps public/release claim flags false.",
            "Post-run intake computes repeat-aware totals for repeat counts 1, 2, 5, 10, 25, 50, 100, 500, and 1000.",
            "No public wording is written until an external review accepts the rerun and a Codex consensus records the exact allowed claim.",
        ),
        "failure_policy": {
            "preserve_failed_artifacts": True,
            "no_scale_down_without_new_packet": True,
            "no_public_claim_from_partial_success": True,
            "no_merge_with_old_warmup1_or_warmup2_rows": True,
            "if_524288_sum_exceeds_time_budget": "Preserve logs and classify as time-budget blocker; do not backfill from the old 524288 warmup=2 evidence.",
        },
        "summary": {
            "command_count": len(commands),
            "planned_scale_count": 2,
            "planned_independent_rows": 8,
            "all_planned_rows_warmup": 3,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "m7_promotion_authorized_before_run": False,
        },
        "goal_level_decision_audit": {
            "decision": "prepare a fresh M7-designated grouped_reduction rerun packet before using pod time",
            "was_i_foolish": "No. The feasibility packet showed that old warmup-asymmetric evidence is not enough for promotion.",
            "foolish_actions": "It would be foolish to rerun ad hoc or reuse old warmup=1/2 rows as a release row.",
            "other_path": "Run the pod immediately. That would risk another unreviewed evidence surface.",
            "different_path_now": "Freeze the rerun contract locally, test it, then seek review before execution.",
        },
    }


def _commands() -> tuple[dict[str, Any], ...]:
    return (
        {
            "id": "env_probe",
            "purpose": "Record GPU, source identity, Python environment, and artifact directory.",
            "command": (
                f"mkdir -p {REMOTE_ART} && nvidia-smi > {REMOTE_ART}/nvidia-smi.txt && "
                f"cat VERSION > {REMOTE_ART}/source_version.txt && "
                f"sha256sum VERSION scripts/v3_0_m28_raydb_prepared_grouped_refresh.py "
                f"scripts/v3_optix_hardware_gate.py scripts/v3_gpu_python_env_gate.py "
                f"scripts/v3_phoenix_grouped_reduction_m7_feasibility.py "
                f"scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py > {REMOTE_ART}/source_manifest.sha256 && "
                f"PYTHONPATH=src:. {REMOTE_PYTHON} scripts/v3_gpu_python_env_gate.py "
                f"--json-out {REMOTE_ART}/gpu_env_gate.json"
            ),
            "required": True,
        },
        {
            "id": "claim_boundary_gate",
            "purpose": "Fail if this packet drifts into release or public-claim authorization before measurement.",
            "command": (
                f"{REMOTE_PYTHON} -c \"import json,pathlib; "
                "p=pathlib.Path('docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json'); "
                "d=json.loads(p.read_text()); "
                "assert d['release_authorized'] is False; "
                "assert d['public_speedup_claim_authorized'] is False; "
                "assert d['whole_app_speedup_claim_authorized'] is False; "
                "assert d['m7_promotion_authorized_before_run'] is False; "
                "print('grouped reduction M7 rerun claim-boundary gate ok')\" "
                f"> {REMOTE_ART}/claim_boundary_gate.txt 2>&1"
            ),
            "required": True,
        },
        {
            "id": "optix_hardware_gate",
            "purpose": "Require NVIDIA OptiX-capable hardware before measuring OptiX rows.",
            "command": (
                f"PYTHONPATH=src:. {REMOTE_PYTHON} scripts/v3_optix_hardware_gate.py "
                f"--require-rt-hardware --json-out {REMOTE_ART}/optix_hardware_gate.json"
            ),
            "required": True,
        },
        {
            "id": "native_build",
            "purpose": "Build native Embree and OptiX libraries for the measured tree.",
            "command": "make build-embree build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0",
            "required": True,
        },
        _measure_command(262144, 1024),
        _measure_command(524288, 2048),
        {
            "id": "post_run_intake",
            "purpose": "Compute repeat-aware totals from the fresh warmup=3 rows.",
            "command": (
                f"PYTHONPATH=src:. {REMOTE_PYTHON} scripts/v3_phoenix_grouped_reduction_m7_feasibility.py "
                f"--fresh-rerun "
                f"--source m7_262144={REMOTE_ART}/m7_grouped_reduction_262144_warmup3.json "
                f"--source m7_524288={REMOTE_ART}/m7_grouped_reduction_524288_warmup3.json "
                f"--json-out {REMOTE_ART}/m7_grouped_reduction_post_run_intake.json "
                f"--md-out {REMOTE_ART}/m7_grouped_reduction_post_run_intake.md"
            ),
            "required": True,
            "generic_capability": "grouped_reduction",
        },
        {
            "id": "artifact_manifest",
            "purpose": "Record final artifact file list after measurement.",
            "command": f"find {REMOTE_ART} -maxdepth 2 -type f | sort > {REMOTE_ART}/artifact_file_index.txt",
            "required": True,
        },
    )


def _measure_command(rows: int, groups: int) -> dict[str, Any]:
    return {
        "id": f"m7_grouped_reduction_{rows}",
        "purpose": f"Run fresh grouped_reduction rows at {rows} generated rows with standardized warmup=3.",
        "command": (
            f"PYTHONPATH=src:. {REMOTE_PYTHON} scripts/v3_0_m28_raydb_prepared_grouped_refresh.py "
            f"--generated-rows {rows} --generated-groups {groups} --modes count,sum "
            f"--backends embree,optix --warmup 3 --include-iteration-walls "
            f"--output {REMOTE_ART}/m7_grouped_reduction_{rows}_warmup3.json"
        ),
        "required": True,
        "generic_capability": "grouped_reduction",
        "generated_rows": rows,
        "generated_groups": groups,
        "warmup": 3,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Grouped-Reduction M7 Rerun Packet",
        "",
        "Status: ready for external review, not executed.",
        "",
        "```text",
        f"release_authorized: {_bool(payload['release_authorized'])}",
        f"public_speedup_claim_authorized: {_bool(payload['public_speedup_claim_authorized'])}",
        f"whole_app_speedup_claim_authorized: {_bool(payload['whole_app_speedup_claim_authorized'])}",
        f"m7_promotion_authorized_before_run: {_bool(payload['m7_promotion_authorized_before_run'])}",
        "```",
        "",
        "## Purpose",
        "",
        "This packet defines the fresh M7-designated grouped_reduction rerun. It does not promote grouped_reduction.",
        "The rerun exists because the feasibility packet found useful evidence but also warmup asymmetry, setup/cold cost, and repeat-policy blockers.",
        "",
        "## Prepared-Query Public Contract Draft",
        "",
    ]
    for rule in payload["prepared_query_public_contract"]["rules"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Planned Rows",
            "",
            "| Row | Generated rows | Groups | Warmup | Output |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["planned_rows"]:
        lines.append(
            f"| `{row['id']}` | {row['generated_rows']} | {row['generated_groups']} | "
            f"{row['warmup']} | `{row['output']}` |"
        )
    lines.extend(
        [
            "",
            "## Required Commands",
            "",
        ]
    )
    for command in payload["required_commands"]:
        lines.append(f"### `{command['id']}`")
        lines.append("")
        lines.append(command["purpose"])
        lines.append("")
        lines.append("```bash")
        lines.append(command["command"])
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Acceptance Checks",
            "",
        ]
    )
    for check in payload["acceptance_checks"]:
        lines.append(f"- {check}")
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            "",
            f"   {audit['was_i_foolish']}",
            "",
            "2. If yes, what actions made the decision foolish?",
            "",
            f"   {audit['foolish_actions']}",
            "",
            "3. Was there another path?",
            "",
            f"   {audit['other_path']}",
            "",
            "4. Can I now try a different path that actually solves the problem?",
            "",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _bool(value: bool) -> str:
    return str(bool(value)).lower()


if __name__ == "__main__":
    raise SystemExit(main())
