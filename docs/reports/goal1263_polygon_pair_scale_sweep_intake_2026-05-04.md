# Goal1263 Polygon Pair Scale Sweep Intake

Date: 2026-05-04

Valid: `True`
Public wording authorized: `False`
Release gate authorized: `False`

This report records a targeted RTX A5000 pod sweep for
`polygon_pair_overlap_area_rows` after Goal1262 identified it as the clearest
v1.1 OptiX/Embree positive candidate. It tests whether the 40k result persists
at larger same-contract scales.

## Artifact

- archive: `docs/reports/goal1263_polygon_pair_scale_sweep_2026-05-04/goal1263_polygon_pair_scale_sweep.tgz`
- sha256: `297d29a9490bff36520d5a27c520cc1f0f47e28d957eb5025a5054704380937c`
- extracted directory: `docs/reports/goal1263_polygon_pair_scale_sweep_2026-05-04/goal1263_polygon_pair_scale_sweep/`
- pod GPU: NVIDIA RTX A5000
- driver: `580.126.09`
- CUDA: `13.0`
- OptiX headers: `NVIDIA/optix-dev` `v8.0.0`

The first sweep attempt wrote OptiX stdout and `--output-json` to the same file,
which corrupted those OptiX JSON files. The retained archive is the clean rerun
with stdout and JSON separated.

## Contract

Same-contract comparison:

- Embree command:
  `python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies N --output-mode summary`
- OptiX command:
  `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies N --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json ...`

Boundary:

- This is RT-assisted positive candidate discovery plus native C++ exact area
  continuation.
- This is not a monolithic GPU polygon overlay kernel.
- This does not authorize whole-app or broad polygon-overlap speedup wording.

## Results

Ratios are `OptiX / Embree`; values below `1.0` mean OptiX is faster.

| Scale | Embree candidate sec | OptiX candidate sec | Candidate ratio | Embree observed pipeline sec | OptiX observed pipeline sec | Pipeline ratio | Parity |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 80000 | `13.658857` | `9.314852` | `0.682` | `25.342276` | `20.963551` | `0.827` | `true` |
| 160000 | `25.554466` | `18.078618` | `0.707` | `49.567778` | `40.407405` | `0.815` | `true` |

Combined with Goal1262:

| Scale | Candidate ratio | Pipeline ratio | Parity |
| ---: | ---: | ---: | --- |
| 10000 | `1.205` | `0.945` | `true` |
| 40000 | `0.835` | `0.791` | `true` |
| 80000 | `0.682` | `0.827` | `true` |
| 160000 | `0.707` | `0.815` | `true` |

## Interpretation

This sweep makes `polygon_pair_overlap_area_rows` the strongest current v1.1
OptiX performance candidate:

- At 40k, 80k, and 160k, OptiX candidate discovery is faster than Embree.
- At 10k, 40k, 80k, and 160k, the observed pipeline is faster than Embree.
- The larger-scale wins are material but bounded: roughly `1.2x` total-pipeline
  speedup and `1.4x` candidate-discovery speedup at 160k.

The evidence is still not public-wording-ready without review because the OptiX
candidate diagnostics report `candidate_count_matches_expected: false` while
summary parity remains `true`. The current contract judges correctness by
summary parity, but public wording needs reviewers to accept that boundary.

Review-required diagnostic clarification:

- For the v1.1 profiler contract, summary parity is the definitive correctness
  gate for this row.
- Candidate-count equality is a secondary diagnostic, not the public
  correctness gate.
- Existing RTDL docs already treat polygon candidate-count mismatch as a
  boundary item for this app family, and the OptiX native code documents
  positive-hit mode as conservative candidate generation with final inclusive
  truth decided on the host.
- The mismatch remains a tracked v1.2 diagnostic-reconciliation item. It blocks
  any stronger unqualified correctness wording, but it does not by itself block
  the bounded positive-candidate interpretation when summary parity is true.

DB caution inherited from Goal1262:

- Do not cite the DB 100k one-shot OptiX ratio `0.900` without also citing the
  100k warm-query ratio `1.270`.
- `database_analytics` remains execution-unblocked but not public-speedup-ready.

## Decision

Codex intake decision:

- `polygon_pair_overlap_area_rows`: `positive_candidate_needs_3_ai_review`

No other v1.1 app row receives new positive wording from this report.

## Next Work

1. Send Goal1262 and Goal1263 to Gemini and Claude for 3-AI review.
2. Ask reviewers specifically whether the polygon-pair claim can be described
   as bounded RT-assisted candidate discovery plus native exact continuation,
   not whole-app polygon overlay acceleration.
3. If accepted, write a consensus file with exact allowed and disallowed
   wording before changing public docs.
4. Track candidate-count diagnostic reconciliation as a v1.2 item before any
   stronger correctness claim.
5. Continue v1.2/v1.5 engineering on generic primitive overhead reduction
   rather than broad exploratory pod runs.

## Boundary

This is Codex intake only. It is not a public claim, not a release gate, and not
3-AI consensus.
