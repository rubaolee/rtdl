# Goal2818 RTNN v2.5 Campaign Checkpoint

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2818 consolidates the RTNN v2.5 work after Goals2810-2817. It does not add
new runtime code. Its purpose is to make the current engineering position
auditable: what RTDL v2.5 added, what the RTX A5000 pod evidence says, what
claims are still blocked, and what the next generic runtime target should be.

## Campaign Question

The RTNN campaign asks whether RTDL can use an app-agnostic fixed-radius
neighbor/ranked-summary primitive to compete with a strong CuPy grid opponent
for nearest-neighbor-style workloads.

The answer is now mostly yes, with one bounded small-row miss:

- At 131K and 262K points, RTDL beats the CuPy grid opponent in all 6 tested
  rows.
- At 32K and 65K points, RTDL beats the CuPy grid opponent in 5 of 6 tested
  rows.
- The only remaining same-contract miss is 32K uniform, where RTDL is at
  0.920x CuPy/RTDL after Goal2817.
- All accepted rows preserve exact ranked-aggregate agreement with the CuPy
  grid opponent.

This is not a public speedup claim. It is an internal v2.5 engineering
checkpoint backed by pod artifacts and external review on the intermediate
steps.

## What v2.5 Added For RTNN

| Goal | Reusable contribution | Effect |
| --- | --- | --- |
| Goal2810 | Generic fixed-radius ranked-summary aggregate path | Stopped materializing per-query witness rows when the user asks only for aggregate summaries. |
| Goal2811 | Density-aware direct aggregate path | Split sparse/direct and dense/two-step execution without adding RTNN-native branches. |
| Goal2812 | Prepared-query aggregate residency | Kept query columns resident across repeats; RTDL timed phases report `upload_sec: 0.0`. |
| Goal2813 | Unsorted bounded top-k summary path | Removed unnecessary ordering work for summary-only top-k rows. |
| Goal2814 | Large-scale same-contract sweep | Showed all 131K/262K uniform, clustered, and shell rows beating CuPy. |
| Goal2815 | Prepared-handle aggregate workspace reuse | Reduced per-call aggregate allocation overhead. |
| Goal2816 | Async reset negative probe | Tested and rejected a generic reset tweak that did not materially help. |
| Goal2817 | Block-partial aggregate path | Reduced global aggregate traffic and moved 65K uniform across parity. |

The native contract remains generic. It uses fixed-radius neighbors, prepared
query points, ranked summaries, aggregate workspaces, and aggregate partials.
It does not introduce an RTNN native ABI or benchmark-specific branch.

## Current Best Pod Evidence

Small rows use the Goal2817 block-partial/current best artifacts.

| Points | Distribution | RTDL median (s) | CuPy grid median (s) | CuPy/RTDL | Status |
| ---: | --- | ---: | ---: | ---: | --- |
| 32768 | uniform | 0.000083132 | 0.000076500 | 0.920x | Still below parity |
| 32768 | clustered | 0.004881053 | 0.011972163 | 2.453x | RTDL faster |
| 32768 | shell | 0.000130961 | 0.000270664 | 2.067x | RTDL faster |
| 65536 | uniform | 0.000138950 | 0.000149633 | 1.077x | RTDL faster |
| 65536 | clustered | 0.018752541 | 0.047126526 | 2.513x | RTDL faster |
| 65536 | shell | 0.000365343 | 0.002722794 | 7.451x | RTDL faster |

Large rows use the Goal2814 scale-sweep artifacts.

| Points | Distribution | RTDL median (s) | CuPy grid median (s) | CuPy/RTDL | Status |
| ---: | --- | ---: | ---: | ---: | --- |
| 131072 | uniform | 0.000302740 | 0.000576740 | 1.905x | RTDL faster |
| 131072 | clustered | 0.067074863 | 0.150910448 | 2.250x | RTDL faster |
| 131072 | shell | 0.002534534 | 0.028577222 | 11.275x | RTDL faster |
| 262144 | uniform | 0.000965423 | 0.003626705 | 3.757x | RTDL faster |
| 262144 | clustered | 0.224376351 | 0.439262436 | 1.958x | RTDL faster |
| 262144 | shell | 0.033773679 | 0.144271217 | 4.272x | RTDL faster |

## Interpretation

The RTNN gap changed shape during this campaign.

Earlier v2.5 rows were not a fair fight because RTDL downloaded too many rows
and paid query-upload cost inside timed repeats. Goals2810 and 2812 corrected
those generic contract problems. Goals2813, 2815, and 2817 then reduced
summary-only work, allocation overhead, and global aggregate traffic.

The remaining 32K uniform miss is now best understood as fixed overhead on a
very sparse small row. The useful work is tiny, so launch/native-call/setup
costs dominate. The fix should not be another RTNN shortcut. The next generic
runtime target is small-row amortization: batched prepared aggregates, CUDA
graph capture, or event-ordered aggregate chaining so repeated aggregate
operations can share setup.

## How Far This Moves v2.5

For the RTNN benchmark app, this campaign is about 85-90% complete:

- the primitive contract is generic and app-agnostic;
- the performance story is strong at realistic larger sizes;
- exact aggregate agreement with CuPy is preserved;
- the remaining miss is narrow and has a clear generic runtime explanation.

For v2.5 as a whole, this does not close the milestone. v2.5 still needs a
cross-benchmark readiness packet that covers Hausdorff/X-HD, spatial RayJoin,
RTNN, RT-DBSCAN, triangle counting, Barnes-Hut, RayDB/librts, partner
selection, neutral-buffer/lifetime discipline, and claim boundaries.

## Recommended Next Step

Do not add an RTNN-specific optimization. The next v2.5 runtime work should be
one of these generic small-row amortization contracts:

1. Batched prepared aggregate calls over one prepared search/query handle.
2. CUDA graph capture for repeated aggregate kernels and small result copies.
3. Event-ordered aggregate chaining so multiple summaries consume the same
   resident inputs without host-side scalar synchronization between phases.

Any of these would help RTNN and should also help other apps with repeated
small continuation phases.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized by this checkpoint.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No package-install claim is authorized.
- No v2.5 release claim is authorized.
- No native app-specific engine customization is introduced.

Goal2818 is a consolidation checkpoint for engineering direction and review,
not a release gate.
