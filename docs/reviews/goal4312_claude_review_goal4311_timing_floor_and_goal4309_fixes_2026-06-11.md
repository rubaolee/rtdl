# Goal4312: Claude Review — Goal4311 Timing-Floor Guard And Goal4309 Fixes

**Reviewer:** Claude (Sonnet 4.6, read-only external follow-up)
**Date:** 2026-06-11
**Scope:** Goal4311 (current scale-profile timing-floor guard) plus follow-up fixes for
Claude Goal4309 findings F-R2, F-R4, F-R5, and F-R6. This is a focused review of a
follow-up packet, not a whole-project review and not a release review.
**Requested by:** External review request for Goal4311 and Goal4309 fix verification.

---

## Verdict: `accept-with-boundary`

Goal4311 correctly closes the first no-pod slice of Fable5 P5/F-R1: it exposes
`hot_path_floor_evaluation` per row and `hot_path_floor_summary` per packet without
authorizing any performance claim. The four statuses are correctly distinguished in the
runner logic and covered by the test suite. The dry-run artifact is a useful pre-pod
policy check.

The four Goal4309 fixes are resolved with one qualification: F-R2 (JSON artifacts in
security guard) is correctly and fully addressed; F-R4 (version mismatch) and F-R5
(tutorial local path) are fully resolved; F-R6 (optix_performance confusion) is
partially addressed — `rt_path_note` is added alongside `inherited_ann_optix_performance_note_present`,
but the original `optix_performance` key persists in the output via `**payload` spread.

The boundary is threefold. First, Goal4311 does not itself produce a runtime packet: the
two floor-targeted rows (`robot_collision`, `raydb_style`) remain at
`requires_runtime_evaluation` until a pod run is completed. No floor-met status should be
read from the dry-run artifact. Second, the historical archive (pre-goal42xx) remains
outside the redaction guard scope; this is unchanged and correctly tracked. Third, the
`optix_performance` field remains in the RTNN Embree output alongside `rt_path_note`; the
field content is a documentation note, not a metric, so the claim risk is cosmetic, but
the partial fix should be acknowledged.

Nothing in this review authorizes a release, public speedup wording, package-install
wording, true-zero-copy wording, broad RT-core wording, automatic partner selection,
whole-app acceleration wording, or paper-reproduction claims.

---

## Findings (ordered by severity)

### F-N1 — LOW: `metric_not_numeric` is used for both missing-path and non-numeric-type cases

In `_evaluate_hot_path_floor` (runner, lines 223–244), when the metric path resolves to
`None` (key absent) and when it resolves to a non-numeric type (e.g., a dict), both cases
produce `"status": "metric_not_numeric"` with `"resolved_metric_value_type"` of
`"NoneType"` and `"dict"` respectively. Additionally, if the stdout file itself is missing,
`_load_json_object` returns `None`, `observed_value` stays `None`, and the same
`metric_not_numeric` status is emitted — even though the root cause is a missing file, not
a non-numeric value.

This is an acceptable scope choice for the current use case: all three cases indicate that
the declared metric path could not be evaluated, and all three should block a floor-met
reading. However, if a future pod run produces a file-missing failure, a downstream reader
who checks only the `status` field will see `metric_not_numeric` rather than a clearer
`stdout_missing` signal. The `resolved_metric_value_type: "NoneType"` field provides
partial disambiguation. Worth documenting as an intentional scope limit in the report or
as a comment at the branch point. No claim boundary implication.

### F-N2 — LOW: Dry-run `hot_path_floor_summary` status `accept` may be misread as a floor pass

In the dry-run artifact, `hot_path_floor_summary["status"]` is `"accept"` because no
confirmed subfloor rows exist yet. The two targeted rows are in `requires_runtime_evaluation`,
not in `subfloor_or_metric_missing_rows`. The boundary field and the `decision_grade_timing_authorized: false`
flag correctly block any performance read. However, a reviewer who scans only the `status`
field at the packet level might read `"accept"` as "floor passed" rather than "no failures
detected in dry-run mode." A future improvement could emit a distinct dry-run status
(`"dry_run_policy_only_no_runtime_evaluation"`) for the summary when `dry_run: true`. This
is a documentation/naming gap only; the claim flags are unambiguously false.

### F-N3 (carries over from F-R6) — LOW: `optix_performance` key persists alongside `rt_path_note`

The F-R6 fix in `rtdl_rtnn_benchmark_app.py` (lines 146–153) captures the inherited
`optix_performance` value from `ann_app`, re-emits it as `rt_path_note`, and sets
`inherited_ann_optix_performance_note_present`. However, the `**payload` spread at line 151
still includes the original `optix_performance` key in the output dict. The
`goal4308_rtnn_embree_front_door_local_linux.json` artifact confirms both keys are present
with identical content. The `optix_performance` field content is a documentation note
(class: `optix_traversal_prepared_summary`; note: explanation text), not a metric, so
there is no measurement confusion. The field name alone creates a cosmetic surface
impression that OptiX performance is being measured in the Embree front door. The F-R6
fix reduces confusion by making `rt_path_note` the canonical name and flagging the
inheritance, but it does not remove the confusing original key. A complete fix would
explicitly exclude `optix_performance` from the spread or pop it from the dict before
returning. No claim boundary implication; no urgency.

---

## Per-Question Answers

### Question 1: Does Goal4311 correctly expose `hot_path_floor_evaluation` per row and `hot_path_floor_summary` per packet?

Yes, fully.

- `_evaluate_hot_path_floor` (runner lines 216–253) is called for every row in both the
  live path (`_run_row` at line 400) and the dry-run path (runner lines 518–533). Each row
  result includes a `hot_path_floor_evaluation` dict.
- `_summarize_hot_path_floor` (runner lines 256–290) is called unconditionally after rows
  are collected (line 571) and writes `hot_path_floor_summary` into the top-level result.
- Both `decision_grade_timing_authorized` and `public_speedup_claim_authorized` are
  hard-coded `False` in both the per-row evaluation and the packet summary. They cannot be
  set `True` by any row's data.
- The dry-run artifact confirms the structure: ten rows each with `hot_path_floor_evaluation`,
  two targeted rows, eight smoke/internal rows, and a packet-level summary boundary string
  that explicitly states rows without a numeric floor are not decision-grade performance
  evidence.
- The test `test_runner_dry_run_exposes_floor_policy_for_all_ten_rows` verifies row count,
  targeted floor rows (exactly the expected two), and that each row's evaluation carries
  `decision_grade_timing_authorized: False`.

No claim exposure from this structure. See F-N2 for the dry-run summary `status: accept`
naming gap.

### Question 2: Is the dry-run behavior useful before pod time is spent?

Yes. The dry-run provides:

1. The intended metric path per row (`representative_hot_path_metric`) — verifiable without
   running the app.
2. The floor target (`hot_path_duration_target_sec`) — shows which rows will be floor-
   evaluated versus smoke/internal when the pod runs.
3. The `requires_runtime_evaluation` status for the two targeted rows — explicitly signals
   that the floor has not yet been tested.
4. The eight smoke/internal rows labeled `smoke_scale_or_internal_not_claim_grade` — a
   reviewer can confirm these are not intended as decision-grade evidence.
5. The packet-level `hot_path_floor_summary` with `targeted_floor_rows` and
   `smoke_or_internal_rows` lists named — a concise policy map for the upcoming pod run.

A reviewer can inspect this artifact to verify that the runner's floor declarations match
the expected policy before committing pod time. This is the correct design for a pre-pod
validation step.

### Question 3: Does the runner correctly distinguish the four statuses?

Yes, with one design note (F-N1).

The four statuses are produced by `_evaluate_hot_path_floor` as follows:

| Status | Condition |
|---|---|
| `floor_met_internal_evidence_only` | Target declared; observed value is numeric and >= target |
| `subfloor_not_claim_grade` | Target declared; observed value is numeric but < target |
| `metric_not_numeric` | Target declared; observed value is absent, non-numeric, or file is missing |
| `smoke_scale_or_internal_not_claim_grade` | No target declared for this row |

The test suite covers all four branches:

- `test_runtime_floor_evaluation_accepts_numeric_metric_at_or_above_target` → `floor_met_internal_evidence_only` (1.25 s observed, 1.0 s target)
- `test_runtime_floor_evaluation_flags_subfloor_or_non_numeric_metrics` → `subfloor_not_claim_grade` (0.25 s observed) and `metric_not_numeric` (dict observed)
- `test_rows_without_floor_are_labeled_smoke_or_internal` → `smoke_scale_or_internal_not_claim_grade`

The naming is semantically accurate: `floor_met_internal_evidence_only` correctly signals
that even a floor-met row is internal evidence, not a public claim. The test at
`test_runtime_floor_evaluation_accepts_numeric_metric_at_or_above_target` line 41
confirms `decision_grade_timing_authorized` remains `False` even when the floor is met.

F-N1: the distinction between path-not-found and non-numeric-type is conflated under
`metric_not_numeric`. This is a documentation gap, not a claim boundary risk.

### Question 4: Did F-R2 expand the security guard to current JSON artifacts without pretending to sanitize the full historical archive?

Yes, fully and correctly.

The updated `goal4303_current_security_redaction_guard_test.py` (lines 44–58) now matches
files with suffix `.json` in addition to `.md` for both `goal42*` and `goal43*` patterns:

```python
if re.match(r"goal42\d", path.name) and path.suffix.lower() in {".md", ".json"}
```

This directly addresses F-R2. The `goal4308_rtnn_embree_front_door_local_linux.json` and
similar JSON artifacts in `docs/reports/` are now included in the redaction scan for the
five live-access-detail patterns (private key header, raw root SSH, working key name,
Windows identity file, raw IPv4 address).

The guard does not claim to cover the historical archive (pre-goal42xx). The test scope
pattern (`goal42\d` and `goal43\d`) preserves the same honest boundary — current surface
only. The historical archive caveat from Goal4303 and from F-R3 of Goal4309 remains open
and correctly not addressed here.

One implementation note: the five redaction patterns are unchanged. The raw IPv4 pattern
(`\b(?:\d{1,3}\.){3}\d{1,3}\b`) will match IP-shaped strings in JSON field values such as
`"platform": "Linux-..."` if any part of the platform string contains a dotted quad. The
current JSON artifacts contain platform strings like `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
which does not match (no dotted quad). The `"executable": "/usr/bin/python3"` contains no
IPv4. Confirmed: zero violations in the current surface.

### Question 5: Did F-R4/F-R5/F-R6 fixes resolve the issues?

**F-R4 (version mismatch): Fully resolved.**

`pyproject.toml` now declares `version = "2.11.0"` (line 7). The active lane is v2.11 and
the runner artifact version label is `rtdl.v2_11.current_embree_cpu_partner_reference.goal4308.v1`.
A user installing the editable package will now see a version consistent with the active
lane. The Goal4307 report documents the update and notes that a fresh pip dry-run was not
available in the current shell; the validation used the source-tree doctor and a
`pyproject.toml` parser test instead. This is honest.

Minor note: `tutorials/current/01_source_tree_first_run.md` line 2 still reads "Status:
current v2.10 source-tree tutorial." The version label in this status line was not updated
to v2.11. This is a cosmetic inconsistency — the tutorial content is correct and the
boundary wording is unchanged — but it compounds a prior stale label.

**F-R5 (tutorial local path): Fully resolved.**

`tutorials/current/01_source_tree_first_run.md` line 21 now reads:
`cd C:\path\to\rtdl_v0_4_release_prep_review`
instead of the hardcoded `C:\Users\Lestat\...` path. The Linux/macOS example at line 14
reads `cd rtdl_v0_4_release_prep_review` (relative directory name), which is portable.
Both forms are now safe for non-local readers.

**F-R6 (optix_performance confusion): Partially resolved — see F-N3.**

The `ann_embree_quality_payload` function now extracts the inherited `optix_performance`
value, re-emits it as `rt_path_note`, and sets `inherited_ann_optix_performance_note_present`
to `True`. The artifact confirms both fields are present with identical content. The
`optix_performance` key is still in the output via `**payload` spread. The `rt_path_note`
companion and the `inherited_ann_optix_performance_note_present` flag materially reduce
confusion for a careful reader. The field content is a documentation note, not a
measurement. No claim boundary implication.

### Question 6: Is the next pod-needed step correctly identified?

Yes.

The Goal4311 report states: "The next pod-required step is a fresh ten-app scale-profile
packet with the updated runner. The desired result is not necessarily that every row meets
a floor; the desired result is that every row is visibly classified as floor-met,
subfloor/not-claim-grade, or smoke/internal."

This framing is correct. It does not over-promise (it does not say all rows will meet the
floor), it does not authorize any claim from the dry-run result, and it correctly identifies
the classification goal (per-row visibility) rather than a pass/fail goal (all rows above
the floor).

The two targeted rows (`robot_collision_optix_scale_default_1024_no_probe_reference` at
target 1.0 s via `run_summary.phase_timing_seconds.traversal.total_sec`, and
`raydb_style_optix_count_scale_default_262k` at target 1.0 s via
`metadata.prepared_phase_timing_summary.native_call_wall.total_sec`) are correctly
identified. The metric paths are specific and the targets are at the same 1-second
aggregate floor established by Goal4266.

---

## Summary Table

| Item | Finding | Verdict |
|---|---|---|
| Goal4311 timing-floor guard | Per-row evaluation and packet summary correct; four statuses correctly distinguished; claim flags hard-false; dry-run useful | accept-with-boundary |
| Goal4311 dry-run summary status | `"status": "accept"` in dry-run mode could be misread as floor pass; boundary fields block any claim read; naming gap only | minor note (F-N2) |
| `metric_not_numeric` scope | Missing file and non-numeric value both map to same status; acceptable scope, worth documenting | minor note (F-N1) |
| F-R2 (JSON in security guard) | Fully resolved; `.json` suffix added to guard scope; pattern unchanged; zero violations in current surface | accept |
| F-R4 (version mismatch) | Fully resolved; `pyproject.toml` now 2.11.0 | accept |
| F-R5 (tutorial local path) | Fully resolved; generic placeholder in place; tutorial status label still says v2.10 (cosmetic only) | accept-with-note |
| F-R6 (optix_performance) | Partially resolved; `rt_path_note` added; `optix_performance` persists via spread; field is a note, not a metric | accept-with-note (F-N3) |
| Next pod step identified | Correct — fresh ten-app packet, per-row classification goal, not a floor-pass goal | accept |

---

## Blocked Claims (unchanged)

This review re-blocks all claims blocked in Goal4302, Goal4309, and Goal4310.

- No release authorization, no tag, no publish action.
- No package-install or `pip install rtdl` wording.
- No broad speedup, whole-application acceleration, or "makes your app faster" wording for
  the ten benchmark apps as a set.
- No broad NVIDIA RT-core, AMD, or Intel GPU performance wording.
- No true-zero-copy or general device-residency wording.
- No paper-reproduction wording for RTNN, RayJoin, X-HD, LibRTS, RT-DBSCAN, or the
  triangle-counting target.
- No automatic partner selection or "RTDL accelerates CuPy/Numba programs" wording.
- No use of `floor_met_internal_evidence_only` status as a basis for public speedup wording.
- The dry-run artifact's `hot_path_floor_summary["status"] == "accept"` does not authorize
  any timing claim; it indicates no confirmed subfloor failures in a pre-runtime pass.

---

*Review boundaries respected: no release authorization, no consensus file, no tags created
or moved, no public speedup/zero-copy/package-install/paper-reproduction claims made, no
source/test/doc changes. Read-only review.*
