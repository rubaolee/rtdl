"""Build Goal5798 S0's single self-contained review entrypoint."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs" / (
    "call_for_review_goal5798_s0_premeasurement_design_freeze_20260823.md")
EMBED = [
    "history/internal_docs/review_goal5797_five_mechanism_liveness_and_semantic_necessity_20260823.md",
    "history/internal_docs/review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md",
    "history/internal_docs/goal5794_to_goal5799_cgo_execution_plan_v2_owl_aware_20260823.md",
    "history/internal_docs/goal5797_a1_postreview_closure_report_20260823.md",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_amendment_a1_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_amendment_a2_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_amendment_a3_20260823.json",
    "history/internal_docs/goal5798_s0_matched_workload_authority_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v2_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v3_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v4_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_independent_verification_20260823.json",
    "history/internal_docs/self_review_goal5798_s0_premeasurement_design_freeze_20260823.md",
    "history/internal_docs/goal5796_pyoptix90_compatibility_successor_result_20260823.json",
    "history/internal_docs/goal5796_source_backed_responsibility_tables_v2_20260823.json",
    "experiments/goal5796_matched/direct_optix.cpp",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5796_matched/rtdl_baseline.py",
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/independent_oracle.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5798_premeasurement/contract_runtime.py",
    "scripts/goal5798_build_premeasurement_freeze.py",
    "scripts/goal5798_verify_premeasurement_freeze.py",
    "tests/goal5798_premeasurement_freeze_test.py",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def language(path: str) -> str:
    return {
        ".json": "json", ".py": "python", ".cpp": "cpp", ".cu": "cuda",
        ".md": "markdown",
    }.get(Path(path).suffix, "text")


def main() -> None:
    members: list[tuple[str, bytes]] = []
    for name in EMBED:
        data = (ROOT / name).read_bytes()
        data.decode("utf-8", errors="strict")
        if not data.endswith(b"\n"):
            raise RuntimeError(f"embedded member lacks terminal LF: {name}")
        if b"`````" in data:
            raise RuntimeError(f"five-backtick collision: {name}")
        members.append((name, data))

    lines = [
        "# Call for external review: Goal5798 S0 premeasurement design freeze",
        "",
        "Date: 2026-08-23",
        "",
        "## Single-file delivery and exact scope",
        "",
        "This Markdown file is the only external delivery file. The controlling",
        "artifact is v4. All predecessors, amendments, critical implementation",
        "sources, independent verification and strict self-review are embedded below.",
        "",
        "This request concerns experimental design only. It requests no host",
        "allocation, functional GPU run, performance worker, timing observation,",
        "performance claim, publication action or submission action.",
        "",
        "Controlling status:",
        "`LOCAL_DESIGN_FROZEN__PHYSICAL_HOST_AND_MEASUREMENT_HARNESS_UNBOUND__EXECUTION_FORBIDDEN`.",
        "",
        "## Requested rulings",
        "",
        "1. Are the two formal workloads large enough for a matched lifecycle case",
        "   study yet still exactly specified and independently reconstructible?",
        "2. Does A2 avoid a straw Direct/PyOptiX baseline by giving A/B/D the same",
        "   sufficient 8,194-row raw-event overflow budget?",
        "3. Is the mandatory B label correct: stock current-source PyOptiX 9.1 on",
        "   R590+, with the OptiX-9.0 compatibility result permanently timing-ineligible?",
        "4. Are cold, preparation, prepared execution, memory, correctness, no-retry",
        "   and phase-attribution boundaries fair and complete?",
        "5. Does the deterministic 24-superblock/all-six-permutation schedule remove",
        "   material run-order bias, and are the paired median/bootstrap rules fixed",
        "   strongly enough to prevent post-result steering?",
        "6. Are RTX 4000 Ada/CC8.9/R590+/non-WSL admission and the explicit rejection",
        "   of lx1, RTX 2000 Ada, cross-machine ratios and other GPU processes correct?",
        "7. Are A1 (VRAM units), A2 (matched raw capacity), and A3 (sampled GPU peak)",
        "   valid pre-result append-only corrections with no scientific result changed?",
        "8. Is the claim ceiling adequate: two designed tasks only; no usability,",
        "   generalization, OWL-performance, universal-performance or success-threshold",
        "   inference?",
        "9. May S0 be accepted as the controlling premeasurement design and permit",
        "   local implementation of the exact phase workers/controller only, while",
        "   host allocation, worker zero and every timing remain unauthorized?",
        "10. What P0/P1/P2/P3 defects remain before an exact execution candidate may",
        "    return for the later worker-zero gate?",
        "",
        "Please answer all ten questions separately and report P0/P1/P2/P3.",
        "A favorable answer must not be interpreted as execution authorization.",
        "",
        "## Facts the ruling must preserve",
        "",
        "- Physical host binding is absent.",
        "- Exact phase-instrumented workers and controller are not implemented.",
        "- Stock PyOptiX 9.1 has not run on the future target.",
        "- GPU sampled peak memory is a lower bound on shorter transients.",
        "- Performance timings, GPU executions and network calls in S0 are all zero.",
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
        "Each five-backtick block contains the exact UTF-8 member bytes. The LF",
        "immediately before the closing fence is the member's terminal LF. Recompute",
        "the manifest digest before using an extracted member.",
        "",
        "## Embedded members",
        "",
    ])
    for name, data in members:
        lines.extend([
            f"### `{name}`", "", f"`````{language(name)}",
            data.decode("utf-8")[:-1], "`````", "",
        ])
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    data = OUT.read_bytes()
    print(f"{sha(data)} {len(data)} {len(members)} {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
