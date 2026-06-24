# Goal2813 RTNN Unsorted Top-K Summary Path

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2813 improves the v2.5 fixed-radius ranked-summary aggregate by separating
summary-only top-k work from sorted row-output work. Goal2812 kept resident
query columns and removed query upload from the timed path, but the summary
kernel still maintained sorted bounded top-k state during traversal. That sort
discipline is needed when a user requests ordered neighbor rows. It is not
needed when the contract only asks for aggregate summary values such as bounded
neighbor count, nearest id checksum, kth id checksum, and distance sum.

This goal changes the float32 summary-only paths to use an unsorted bounded
top-k helper. Each candidate is compared against the current worst slot, inserted
only when useful, and the nearest/kth summary fields are recovered by a final
bounded scan over the small local buffer. The native engine remains app-name-free:
the implementation is a generic fixed-radius 3D ranked-summary optimization, not
an RTNN-specific shortcut.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_core.cpp` | Added `frn_ranked_insert_unsorted_f32(...)` plus summary finalization scans for nearest/kth fields. |
| `tests/goal2813_rtnn_unsorted_topk_summary_test.py` | Guards that summary-only float32 paths use the unsorted helper, validates pod artifacts, and checks the report boundary. |
| `docs/reports/goal2813_rtnn_unsorted_topk_summary_pod/*.json` | Clean pod timing artifacts for 32K and 65K RTNN same-contract rows. |

The sorted helper remains available for row-output paths. Goal2813 only changes
the summary-only float32 kernels.

## Clean Pod Evidence

Clean-from-Git pod:

```text
commit: 73270996cdeaff24cc7f90c7773818cccec73a8b
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX SDK: /root/vendor/optix-sdk
OptiX library: /root/rtdl_goal2785_work/build/librtdl_optix.so
focused tests: 21 passed
```

Final clean-head guard after report/artifact commit:

```text
commit: 27ab586ef3454e85cd2ef1457a4e151417bf2132
source_dirty: []
focused tests: 24 passed
```

Artifacts:

- `docs/reports/goal2813_rtnn_unsorted_topk_summary_pod/rtnn_unsorted_topk_median_f32_32768.json`
- `docs/reports/goal2813_rtnn_unsorted_topk_summary_pod/rtnn_unsorted_topk_median_f32_65536.json`

Both artifacts report clean provenance, median timing, `upload_sec: 0.0`, exact
ranked aggregate agreement with the CuPy grid opponent, and no authorized public
speedup claim.

## Median Timing Results

Compared with Goal2812 prepared-query median timing:

| Points | Distribution | Goal2812 RTDL median (s) | Goal2813 RTDL median (s) | RTDL change | Goal2813 CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: | ---: |
| 32768 | uniform | 0.000135981 | 0.000145571 | 0.934x | 0.575x |
| 32768 | clustered | 0.016044247 | 0.004760874 | 3.370x | 2.514x |
| 32768 | shell | 0.000390197 | 0.000151183 | 2.581x | 1.746x |
| 65536 | uniform | 0.000419207 | 0.000184891 | 2.267x | 0.863x |
| 65536 | clustered | 0.063771570 | 0.019996277 | 3.189x | 2.360x |
| 65536 | shell | 0.002772068 | 0.000366806 | 7.557x | 7.419x |

RTDL is faster than the CuPy grid opponent in 4 of 6 rows under this controlled
same-contract benchmark: both clustered rows and both shell rows. The uniform
rows are still mixed: 32K uniform remains slower, and 65K uniform is closer but
still below parity.

## Interpretation

The key lesson is that the primitive contract needs to distinguish ordered
neighbor rows from aggregate summaries. A runtime that always preserves sorted
top-k rows pays unnecessary per-candidate maintenance cost when the user only
needs summary fields. The unsorted bounded top-k path is a reusable generic
optimization because it is driven by the requested output contract, not by an
application name.

Dense clustered cases improve because many candidate updates previously paid a
sorted-shift cost. Shell cases improve because the direct single-kernel path now
does less work per accepted candidate. The remaining uniform gap is likely launch
and occupancy overhead relative to CuPy on small, sparse rows, not a data-copy
problem: query upload is already zero inside the timed RTDL phase.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized before external review.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No package-install claim is authorized.
- No native app-specific engine customization is introduced.

This is strong internal evidence that the v2.5 primitive/runtime direction is
working for RTNN-like rows, but it still needs external review before any public
performance wording is promoted.
