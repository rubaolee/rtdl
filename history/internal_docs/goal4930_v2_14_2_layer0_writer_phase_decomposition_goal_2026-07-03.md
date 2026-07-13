# Goal4930: v2.14.2 Layer 0 Writer Phase Decomposition

Date: 2026-07-03

Status: `planned_pending_review`

## Purpose

Start v2.14.2 with measurement, not implementation.

The RayJoin v2.14.1 app is correct and packaged, but the remaining hot-path
cost is dominated by Python-side output work. Before building any new
performance feature, Goal4930 must separate the writer/output path into
measured subphases so the next optimization is aimed at a real bottleneck.

## Non-Goals

Goal4930 does not:

- add a new RTDL primitive;
- change RTDL runtime/native code;
- change the public RayJoin result format;
- claim a speedup;
- implement device-resident row buffers;
- implement compiled writer/output assembly;
- start Layer 1, Layer 2, or Layer 3.

## Input Baseline

Use the v2.14.1 RayJoin paper app:

`Paper-reproduction-apps/rayjoin-paper/`

Use the public County x Soil sample first, because it has:

- public inputs;
- public answer file;
- AuthorOfficial comparator;
- RTDL byte-equality evidence;
- RTDL+Numba byte-equality evidence.

## Measurement Questions

Goal4930 answers only these questions:

1. In the current Section 5.7 RTDL path, how much time is spent in structural
   output-chain assembly versus final text/byte formatting?
2. How much time is spent in reprojection, sort, grouping, and dedupe after the
   public LSI/PIP primitives have already returned their rows?
3. How much of the current writer cost is numeric/array-shaped and therefore
   plausibly reusable in a generic compiled output path?
4. How much is tied to the RayJoin paper's exact text/output-chain format and
   therefore should remain app-owned?
5. Are the previous hot/cold conclusions still consistent when measured in one
   run with one phase-accounting vocabulary?

## Required Phase Ledger

The completion report must include a table with at least:

| Phase | Required Measurement |
| --- | --- |
| LSI public primitive replay | seconds, row count |
| midpoint/reprojection numeric transform | seconds, row count |
| sort/order preparation | seconds, row count |
| PIP public primitive replay | seconds, point count |
| output-chain structural assembly | seconds, chain count |
| text/byte formatting | seconds, output byte count |
| file write / flush | seconds, output path |
| total hot body | seconds |
| total query+output | seconds |

If a phase cannot be isolated without changing product code, report that
explicitly and measure the closest safe boundary.

## Correctness Gate

Every measured run must keep the existing Section 5.7 public-sample correctness
gate:

- AuthorOfficial output equals public answer;
- RTDL output equals public answer;
- output SHA-256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`.

Performance numbers without byte-equality are not evidence.

## Classification Gate

At the end, classify the next optimization target as exactly one of:

- `structure_assembly_dominant`: continue toward a generic compiled output
  assembly layer;
- `text_formatting_dominant`: stop broad engine work for this bottleneck; the
  remaining cost is app-format-specific unless a general output-format compiler
  is justified separately;
- `numeric_transform_dominant`: continue toward generic array/device numeric
  continuation work;
- `mixed_no_single_bottleneck`: do not implement; write a narrower measurement
  plan;
- `measurement_inconclusive`: stop and fix instrumentation.

## Genericity Rule

RayJoin is the exam, not the model.

Any proposed v2.14.2 optimization after Goal4930 must state whether it is:

- generic to spatial pipelines;
- generic to output grouping/assembly;
- generic to numeric continuations;
- RayJoin-format-specific.

RayJoin-format-specific work may remain in the RayJoin paper app, but it must
not be sold as RTDL engine progress.

## Expected Outcome

The likely useful outcome is a measured split of the current writer cost:

- if structural assembly is large, Layer 3 has a real generic target;
- if text formatting dominates, the honest next step is to stop broad engine
  work for RayJoin's remaining gap and leave the final formatting layer
  app-owned;
- if numeric transform/sort dominates, Layer 2 has a bounded target.

## Exit Criteria

Goal4930 is complete only when it produces:

1. a phase ledger with raw artifacts;
2. byte-equality proof for every timed run;
3. a classification label from the allowed set above;
4. a next-step recommendation that follows from the measurements;
5. a call-for-review packet for external audit.

## Exit Labels

Allowed labels:

- `complete_structure_assembly_dominant_authorize_layer3_design`
- `complete_text_formatting_dominant_stop_engine_work_for_writer`
- `complete_numeric_transform_dominant_authorize_layer2_design`
- `complete_mixed_no_single_bottleneck_write_narrower_measurement`
- `blocked_measurement_inconclusive`
