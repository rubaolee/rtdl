from __future__ import annotations

import json
import re
import shlex
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from scripts.goal410_tutorial_example_check import public_cases


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = [
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/release_facing_examples.md"),
    Path("examples/README.md"),
    *sorted(Path("docs/tutorials").glob("*.md")),
]

GOAL513_COMMANDS = [
    "python examples/rtdl_hello_world.py",
    "python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16",
    "python examples/rtdl_feature_quickstart_cookbook.py",
    "python examples/rtdl_ray_triangle_any_hit.py",
    "python examples/rtdl_visibility_rows.py",
    "python examples/rtdl_reduce_rows.py",
    "python examples/rtdl_graph_bfs.py --backend cpu_python_reference",
    "python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference",
    "python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference",
    "python examples/rtdl_db_grouped_count.py --backend cpu_python_reference",
    "python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference",
    "python examples/rtdl_v0_7_db_app_demo.py --backend auto",
    "python examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto",
    "python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference",
    "python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference",
    "python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference",
]

GOAL593_COMMANDS = [
    "python examples/rtdl_hiprt_ray_triangle_hitcount.py",
    "python examples/rtdl_apple_rt_closest_hit.py",
    "python examples/rtdl_apple_rt_visibility_count.py",
]

PUBLIC_VALIDATION_COMMAND_KEYS = {
    ("python -m unittest", "default"): "postgresql_validation_command",
}


@dataclass(frozen=True)
class CommandRecord:
    path: str
    line: int
    command: str
    normalized: str
    program: str
    backend: str
    classification: str
    coverage: str


def iter_logical_lines(path: Path) -> Iterable[tuple[int, str]]:
    pending = ""
    start_line = 0
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if pending:
            pending = f"{pending} {line}"
        else:
            pending = line
            start_line = lineno
        if pending.endswith("\\") or pending.endswith("^") or pending.endswith("`"):
            pending = pending[:-1].strip()
            continue
        yield start_line, pending
        pending = ""
    if pending:
        yield start_line, pending


def normalize_command(line: str) -> str | None:
    line = line.strip().strip("`")
    line = re.sub(r"^\$ ", "", line)
    if line.startswith(("set PYTHONPATH", "$env:PYTHONPATH", "PYTHONPATH=")):
        if " python" not in f" {line}" and not line.startswith("PYTHONPATH="):
            return None
    if "python" not in line:
        return None
    is_public_program = any(fragment in line for fragment in ("examples/", "examples\\", "scripts/", "scripts\\"))
    is_public_validation = "RTDL_POSTGRESQL_DSN" in line and "python -m unittest" in line
    if not is_public_program and not is_public_validation:
        return None
    line = line.replace("\\", "/")
    line = re.sub(r"\bPYTHONPATH=[^ ]+\s+", "", line)
    line = re.sub(r"\bRTDL_POSTGRESQL_DSN=\"[^\"]*\"\s+", "", line)
    line = re.sub(r"\bRTDL_POSTGRESQL_DSN='[^']*'\s+", "", line)
    line = re.sub(r"\bRTDL_POSTGRESQL_DSN=[^ ]+\s+", "", line)
    match = re.search(r"\bpython(?:3(?:\.\d+)?)?\b\s+(.+)$", line)
    if not match:
        return None
    command = "python " + match.group(1).strip()
    return " ".join(command.split())


def command_key(command: str) -> tuple[str, str]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    program = ""
    backend = "default"
    if len(tokens) >= 3 and tokens[1] == "-m" and tokens[2] == "unittest":
        program = "python -m unittest"
    else:
        for token in tokens[1:]:
            if token.endswith(".py") and (token.startswith("examples/") or token.startswith("scripts/")):
                program = token
                break
    if "--backend" in tokens:
        index = tokens.index("--backend")
        if index + 1 < len(tokens):
            backend = tokens[index + 1]
    return program, backend


def harness_command(entry: dict[str, object]) -> str:
    return "python " + " ".join(str(arg) for arg in entry["args"])


def build_coverage_maps() -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    exact_keys: dict[str, str] = {}
    family_keys: dict[tuple[str, str], str] = {}
    for entry in public_cases():
        command = harness_command(entry)
        exact_keys[command] = "goal410_harness_exact"
        family_keys[command_key(command)] = "goal410_harness_family"
    for command in GOAL513_COMMANDS:
        exact_keys.setdefault(command, "goal513_front_page_smoke_exact")
        family_keys.setdefault(command_key(command), "goal513_front_page_smoke_family")
    for command in GOAL593_COMMANDS:
        exact_keys.setdefault(command, "goal593_public_example_smoke_exact")
        family_keys.setdefault(command_key(command), "goal593_public_example_smoke_family")
    family_keys.update(PUBLIC_VALIDATION_COMMAND_KEYS)
    return exact_keys, family_keys


def classify(program: str, backend: str, command: str, raw_command: str) -> str:
    if backend in {"optix", "vulkan"}:
        return "linux_gpu_backend_gated"
    if "RTDL_POSTGRESQL_DSN" in raw_command or "postgresql" in command.lower():
        return "linux_postgresql_gated"
    if program.startswith("examples/visual_demo/") or "render_hidden_star_chunked_video.py" in program:
        return "visual_demo_or_optional_artifact"
    if backend in {"cpu", "embree"}:
        return "optional_native_backend_gated"
    return "portable_python_cpu"


def audit() -> dict[str, object]:
    exact_coverage_keys, family_coverage_keys = build_coverage_maps()
    records: list[CommandRecord] = []
    for rel_path in PUBLIC_DOCS:
        full_path = ROOT / rel_path
        if not full_path.exists():
            continue
        for line, raw_command in iter_logical_lines(full_path):
            normalized = normalize_command(raw_command)
            if normalized is None:
                continue
            program, backend = command_key(normalized)
            if not program:
                continue
            coverage = exact_coverage_keys.get(normalized)
            if coverage is None:
                coverage = family_coverage_keys.get((program, backend), "not_mechanically_covered")
            records.append(
                CommandRecord(
                    path=str(rel_path),
                    line=line,
                    command=raw_command,
                    normalized=normalized,
                    program=program,
                    backend=backend,
                    classification=classify(program, backend, normalized, raw_command),
                    coverage=coverage,
                )
            )
    uncovered = [record for record in records if record.coverage == "not_mechanically_covered"]
    coverage_counts = Counter(record.coverage for record in records)
    classification_counts = Counter(record.classification for record in records)
    return {
        "valid": not uncovered,
        "public_doc_count": len([path for path in PUBLIC_DOCS if (ROOT / path).exists()]),
        "command_count": len(records),
        "coverage_counts": dict(sorted(coverage_counts.items())),
        "classification_counts": dict(sorted(classification_counts.items())),
        "uncovered": [asdict(record) for record in uncovered],
        "commands": [asdict(record) for record in records],
    }


def write_markdown(payload: dict[str, object], path: Path) -> None:
    lines = [
        "# Goal515 Public Command Truth Audit",
        "",
        "Date: 2026-04-17",
        "",
        f"- Valid: `{str(payload['valid']).lower()}`",
        f"- Public docs scanned: `{payload['public_doc_count']}`",
        f"- Runnable public commands found: `{payload['command_count']}`",
        "",
        "## Coverage Counts",
        "",
    ]
    for key, value in dict(payload["coverage_counts"]).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Classification Counts", ""])
    for key, value in dict(payload["classification_counts"]).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Uncovered Commands", ""])
    uncovered = list(payload["uncovered"])
    if uncovered:
        for record in uncovered:
            lines.append(
                f"- `{record['path']}:{record['line']}` `{record['normalized']}`"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Command Inventory", ""])
    for record in payload["commands"]:
        lines.append(
            f"- `{record['path']}:{record['line']}` "
            f"`{record['normalized']}` -> `{record['classification']}` / `{record['coverage']}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = audit()
    report_dir = ROOT / "docs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "goal515_public_command_truth_audit_2026-04-17.json"
    md_path = report_dir / "goal515_public_command_truth_audit_2026-04-17.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, md_path)
    print(json.dumps({key: payload[key] for key in ("valid", "public_doc_count", "command_count", "coverage_counts", "classification_counts")}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
