# Goal4185 Short-Row Stress Calibration on RTX 4000 Ada

Date: 2026-06-09

Status: internal measurement-adequacy evidence

## Purpose

Goal4182 proved the current 10-app scale packet runs cleanly, but several rows
were still short smoke/scale rows. Goal4185 probes the short rows with larger
repeat or scale settings to separate real runtime bottlenecks from measurement
adequacy gaps.

This is not a public speedup report and does not authorize release claims. Its
main value is telling us which benchmark front doors are already suitable for
second-level hot-path evidence and which need better aggregate timing fields.

## Pod And Source

- Pod: `ssh root@157.157.221.29 -p 24101 -i ~/.ssh/id_ed25519`
- Effective RTDL working key used by Codex: `id_ed25519_rtdl_codex`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit: `79afb95a65bfb7a359efb56210294c89ec210060`
- Artifact directory: `docs/reports/goal4185_short_row_stress_calibration_rtx4000ada/`

## Results

| Row | Stress setting | Wrapper sec | Reported hot-path signal | Adequacy reading |
| --- | --- | ---: | --- | --- |
| Hausdorff/X-HD | `copies=8192`, `repeat=200`, `warmup=5` | 18.997 | measured query total `17.036169s`; median-style legacy key `0.066711s` | Adequate second-level repeated-query evidence, but consumers must use `repeat_protocol.measured_query_total_sec`, not the legacy median-style `run_phases` key. |
| Contact manifold | `grid=64`, `repeat-count=10000` | 0.630 | native collect `0.000459s` | Not claim-grade yet: the front door does not expose repeat-aware aggregate timing or repeat metadata for this mode. |
| LibRTS spatial index | `repeat=40`, `warmup=2` | 3.512 | query total `1.749403s`, median `0.043698s` | Adequate second-level repeated-query evidence. |
| RTNN | `repeat=5000` | 4.061 | elapsed-run aggregate `0.853672s`; median `0.000170s`, repeat `5000` | Aggregate data exists, but this setting is just under the one-second hot-path target; increase repeat before claim-grade timing. |
| Triangle counting | `repeat=10000`, `warmup=10` | 2.837 | backend run total `2.063972s`, query median `0.140332ms` | Adequate second-level repeated-query evidence. |

## Engineering Meaning

The next major work is not another isolated app tweak. It is benchmark/runtime
measurement hardening:

- Teach current packet consumers to read Hausdorff/X-HD aggregate timing from
  `repeat_protocol.measured_query_total_sec` rather than the legacy median-style
  `run_phases` key.
- Raise the RTNN stress repeat beyond `5000` when claim-grade second-level
  aggregate timing is required.
- Fix or clarify `contact_manifold` native-collect repeat semantics so the
  public front door can report repeat count and aggregate native-collect time.
- Keep LibRTS, triangle counting, and Hausdorff/X-HD in the second-level evidence
  lane; their stress rows already expose aggregate totals.

This keeps the project aligned with the language/runtime goal: build generic
RTDL primitives and partner contracts with transparent measurement, rather than
hand-tuning app stories one row at a time.

## Boundary

Goal4185 does not change the current route registry and does not authorize public performance claims. It defines the next measurement-hardening targets
needed before a future major release can present all benchmark apps with
consistent long-duration evidence.
