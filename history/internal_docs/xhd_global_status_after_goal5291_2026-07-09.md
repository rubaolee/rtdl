# X-HD Global Status After Goal5291

Date: 2026-07-09

## Objective

The active objective remains full X-HD paper reproduction:

```text
The final Python / RTDL / partner implementation should reproduce the author
C++ / CUDA / OptiX implementation functionally, and the project should provide
a comprehensive performance evaluation.
```

This objective is not complete. The current evidence is strong for one public
same-source representative workload, but not for exact paper datasets or full
Figure 5-11 reproduction.

## Current Position

### Completed And Externally Reviewed

```text
Level A bounded same-input correctness: complete through Goal5126.
Generic nearest / witness / reduction extraction: complete through Goal5128.
Full-reproduction plan: reviewed and amended through Goal5129.
Midterm status after Goal5216: reviewed, amended, and sign-off verified.
```

The midterm sign-off allows the following narrow summary:

```text
RTDL has one Level-B same-source representative X-HD workload on public
Stanford Dragon -> HappyBuddha. RTDL matches the author binary re-run directed
Hausdorff scalar on that public data to about 2.38e-9.
```

### Strongest Current Value Evidence

Workload:

```text
public Stanford Dragon -> HappyBuddha
source points = 437,645
target points = 543,652
```

Values:

```text
paper-branch log HDResult = 0.12572969496250153
author re-run HDResult    = 0.12572988867759705
RTDL route HDResult       = 0.12572988629271128

RTDL vs author re-run abs diff      ~= 2.38e-9
author re-run vs paper-log abs diff ~= 1.94e-7
```

Interpretation:

```text
RTDL matches the author re-run on public same-source data.
RTDL does not directly match the paper log.
The author re-run itself differs from the paper log, consistent with public
input non-identity.
```

### Exact-Value-Only Caveat

The current fastest Dragon -> HappyBuddha route uses the Goal5211 generic
global-bound early-break path. It is exact for the directed-Hausdorff scalar
value, but not for every per-source witness:

```text
global_bound_early_break_count = 409,376 / 437,645 sources (~93.5%)
per_source_witness_exact = false
```

Therefore the route may be used for scalar directed-HD value reproduction under
the stated contract, but it must not be presented as exact per-source nearest
witness reproduction.

## Current Performance Evidence

Current representative Dragon -> HappyBuddha route:

```text
fresh RTDL route wall              ~= 0.852s
fresh full gate including input    ~= 1.531s
explicit-warm measured route       ~= 0.288s
```

These are RTDL route/process denominators. They are not directly comparable to
the author paper-log `Running.AvgTime` or to author process wall without a
separate denominator-alignment review.

No author-vs-RTDL performance ratio is currently authorized.

## Figure Status

### Figure 5

Current packet:

```text
history/internal_docs/call_for_review_goals5288_5291_xhd_figure5_packet_2026-07-09.md
```

Packet status:

```text
ready_for_external_review
```

Current conclusion before review:

```text
Dragon -> AsianDragon: no-go under current available inputs.
Dragon -> HappyBuddha: value-matched Level-B graphics candidate.
Figure 5 full reproduction: false.
Author-vs-RTDL performance ratio: false.
Exact paper dataset identity: false.
```

### Figure 6

Current packet:

```text
history/internal_docs/call_for_review_goals5268_5271_xhd_figure6_packet_2026-07-09.md
```

Packet status:

```text
ready_for_external_review
```

Current conclusion before review:

```text
Figure 6 reproduced = false
exact input blocker = true
Level-B pruning diagnostic allowed = true
lb=2048 substitute authorized as Figure 6 = false
```

The current exact Figure 6 paths under `/local/storage/shared/HDDatasets` are
not available on the POD. The available Level-B Dragon -> AsianDragon candidate
does not support the paper's `lb=256` Figure 6 setting cleanly.

## Claim Boundary

Allowed:

```text
One public Dragon -> HappyBuddha Level-B same-source representative scalar
directed-HD value matches the author re-run.
Figure 5 has one value-matched graphics candidate.
Figure 6 has an author-side Level-B pruning diagnostic, not a Figure 6
reproduction.
```

Forbidden:

```text
Full X-HD paper reproduction is complete.
Exact paper dataset identity is proved.
RTDL matches the paper log directly.
Broad Level-B reproduction across all paper workload families is complete.
Figure 5 is reproduced.
Figure 6 is reproduced.
Author-vs-RTDL performance parity, speedup, or ratio is established.
Exact per-source witnesses are reproduced by the early-break route.
Warm-only timings are the performance headline.
```

## Next Work Plan

### Step 1: External review before claim promotion

Send these packets for strict review:

```text
history/internal_docs/call_for_review_goals5288_5291_xhd_figure5_packet_2026-07-09.md
history/internal_docs/call_for_review_goals5268_5271_xhd_figure6_packet_2026-07-09.md
```

No Figure 5 / Figure 6 claim status should be upgraded before review.

### Step 2: Decide the next paper blocker

After review, choose exactly one branch:

```text
A. Continue Figure 5:
   Acquire / validate BraTS, geo, and remaining graphics input provenance.
   Run cheap author value prechecks before any expensive RTDL route.

B. Continue Figure 6:
   Keep it as a Level-B pruning diagnostic unless exact paper inputs appear.
   Do not substitute lb=2048 for paper lb=256.

C. Move to another figure:
   Audit Figure 7 / Figure 8 / Figure 10 author-log semantics and source
   scripts before writing new RTDL route code.

D. Exact input acquisition:
   Focus on recovering paper dataset files, hashes, or equivalent provenance.
```

### Step 3: Avoid route micro-optimization until the paper blocker is chosen

The current route already has a strong scalar-value result for one workload.
Further micro-optimization is lower priority than deciding whether the next
paper blocker is input provenance, Figure 5 coverage, Figure 6 diagnostics, or
another figure's author-log semantics.

## POD Use Expectation

No POD is required for the immediate review / documentation step.

Use the POD only for:

```text
new author value prechecks;
new RTDL full-route executions;
same-POD author / RTDL gates;
new figure-specific source-script probes.
```

Always use the wrapper:

```powershell
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Before any expensive RTDL execution, run a cheap author-only value precheck
where possible. Do not spend route time on a candidate that fails value
matching at the author-only stage.

## Recommended Immediate Action

Send the Figure 5 and Figure 6 packets for strict review. If no reviewer is
available, the next implementation work should be a low-cost source/log audit
for the next figure, not a new performance tuning pass.
