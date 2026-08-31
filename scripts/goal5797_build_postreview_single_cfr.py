"""Build the single-file Goal5797-A1 external review entrypoint."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs" / (
    "call_for_review_goal5797_a1_postreview_leaf_oracle_and_provenance_"
    "closure_20260823.md")

EMBED = [
    "history/internal_docs/goal5797_a1_postreview_closure_report_20260823.md",
    "history/internal_docs/goal5797_a1_exhaustive_populated_leaf_liveness_preaction_20260823.json",
    "history/internal_docs/goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json",
    "history/internal_docs/goal5797_a1_exhaustive_populated_leaf_liveness_independent_verification_20260823.json",
    "history/internal_docs/goal5797_a1_oracle_counterfactual_and_source_provenance_result_20260823.json",
    "history/internal_docs/goal5797_a1_oracle_counterfactual_and_source_provenance_independent_verification_20260823.json",
    "history/internal_docs/goal5797_five_mechanism_liveness_and_necessity_result_20260823.json",
    "history/internal_docs/goal5797_gpu_evidence_20260823/GOAL5797_PYOPTIX_CONTROLS.json",
    "history/internal_docs/goal5797_gpu_evidence_20260823/GOAL5797_INDEPENDENT_PTX_RECOMPILE.json",
    "history/internal_docs/goal5797_gpu_evidence_20260823/pyoptix_controls_v2_executed.py",
    "history/internal_docs/goal5796_source_backed_responsibility_tables_v2_20260823.json",
    "history/internal_docs/goal5796_pyoptix90_compatibility_successor_result_20260823.json",
    "history/internal_docs/goal5796_home_pyoptix90_compatibility_evidence_20260823/results/TRANSACTION_RESULT.json",
    "history/internal_docs/goal5796_home_pyoptix90_compatibility_evidence_20260823/results/PYOPTIX_ORACLE.json",
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/independent_oracle.py",
    "scripts/goal5797_build_exhaustive_leaf_liveness.py",
    "scripts/goal5797_verify_exhaustive_leaf_liveness.py",
    "scripts/goal5797_build_postreview_oracle_and_provenance.py",
    "scripts/goal5797_verify_postreview_oracle_and_provenance.py",
    "tests/goal5797_a1_exhaustive_leaf_liveness_test.py",
    "tests/goal5797_a1_oracle_and_provenance_test.py",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def language(path: str) -> str:
    suffix = Path(path).suffix
    return {".json": "json", ".py": "python", ".cu": "cuda", ".md": "markdown"}.get(
        suffix, "text")


def main() -> None:
    members: list[tuple[str, bytes]] = []
    for name in EMBED:
        path = ROOT / name
        data = path.read_bytes()
        data.decode("utf-8", errors="strict")
        members.append((name, data))

    lines = [
        "# Call for external review: Goal5797-A1 post-review closure",
        "",
        "Date: 2026-08-23",
        "",
        "## Delivery rule",
        "",
        "This Markdown file is the **only external delivery file**.  Every new",
        "closure artifact and the minimum prior evidence needed to inspect it is",
        "embedded byte-for-byte below.  Do not send a packet or a second file.",
        "",
        "No GPU program was re-executed for A1, registered performance timing count",
        "is zero, Goal5798 timing is unauthorized, and `lx1` is not a performance host.",
        "",
        "## Requested rulings",
        "",
        "1. Does the frozen-before-sweep, exact 19/19 populated-leaf experiment close",
        "   P1-1, including `role_effects.finalize[1] -> require_status_ok`?",
        "2. Does the explicit 0/5 platform, 5/5 registered-input oracle, 5/5 prelaunch",
        "   gate comparison close P1-2 without implying that developer tests are",
        "   unnecessary?",
        "3. Is the source origin now unambiguous: hand-written matched CUDA source,",
        "   shared by Direct/PyOptiX, exact Goal5797 textual variants, not RTDL-generated?",
        "4. Are the Pascal, CP004, physical-mutation and B/B guard limitations correctly",
        "   stated, with no broader claim?",
        "5. May Goal5797 be considered complete at the exact five-mechanism, two-designed-",
        "   task, current-source-PyOptiX-compatibility, non-performance scope?",
        "6. If and only if the above passes, may Goal5798 proceed to premeasurement",
        "   design/freeze only?  This question does not request timing authorization.",
        "",
        "Please report P0/P1/P2/P3 and answer all six questions separately.",
        "",
        "## Claim ceiling",
        "",
        "A1 does not create new-application generalization, usability, productivity,",
        "performance, RT-core-execution, OWL-execution, stock-PyOptiX-9.1, universal",
        "correctness or oracle-free-correctness evidence.  The corresponding counts",
        "remain zero where applicable.",
        "",
        "## Embedded-member manifest",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for name, data in members:
        lines.append(f"| `{name}` | {len(data)} | `{sha(data)}` |")
    lines.extend([
        "",
        "## Reconstruction convention",
        "",
        "For each member, copy the bytes between its four-backtick fences exactly as",
        "UTF-8.  Every embedded source file ends with a terminal LF; the terminal LF",
        "immediately before the closing fence belongs to the member.  Recompute the",
        "manifest SHA-256 before using the member.",
        "",
        "## Embedded members",
        "",
    ])
    for name, data in members:
        text = data.decode("utf-8")
        if "````" in text:
            raise RuntimeError(f"four-backtick fence collision: {name}")
        lines.extend([
            f"### `{name}`",
            "",
            f"````{language(name)}",
            text[:-1] if text.endswith("\n") else text,
            "````",
            "",
        ])
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    data = OUT.read_bytes()
    print(f"{sha(data)} {len(data)} {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
