# Goal5289 - X-HD Figure 5 Bounded Same-POD Probe

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5288 showed that Figure 5 has strong author timing-log coverage but lacks a
denominator-aligned RTDL/author matrix. Goal5289 tests one bounded same-POD
graphics candidate to see whether a Figure 5 subset can be compared directly.

This is a probe, not a Figure 5 reproduction claim.

## POD

POD preflight:

```text
POD_OK
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Used wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 ...
```

No naked SSH was used.

## Input

Level-B public/same-source graphics candidate:

```text
/tmp/xhd_goal5234/data/dragon.ply
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
```

This is not exact paper byte-input identity.

## Author Run

Author command used:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
  -input1=/tmp/xhd_goal5234/data/dragon.ply
  -input2=/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
  -n_dims=3
  -input_type=ply
  -variant=rt
  -execution=gpu
  -normalize=false
  -repeat=1
  -check=false
```

Author result:

```text
HDResult = 0.06545527279376984
Running.AvgTime = 18.436 ms
EB = true
Prune = true
LB = 256
NumPointsPerCell = 15
process wall ~= 2.095 s
```

## RTDL Run

RTDL command used:

```text
python /tmp/rtdl_goal5281/Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
  -input1 /tmp/xhd_goal5234/data/dragon.ply
  -input2 /tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
  -n_dims 3
  -input_type ply
  -variant rt
  -execution gpu
  --rtdl-route cell-mbr-fast-scalar
  --author-float32-normalization
  --translate-each-input-to-min-bound
  --tolerance 1e-5
  -check false
```

RTDL result:

```text
HDResult = 0.06536787240753439
process wall ~= 261.970 s
```

## Decision

The bounded same-POD probe is a no-go for Figure 5 comparison:

```text
abs_diff = 8.740038623544777e-05
matched_value = false
same_denominator_ratio_allowed = false
```

Why:

```text
The author default X-HD/LB=256 path on this Level-B scaled candidate returns the
same wrong candidate value previously observed in Figure 6 diagnostics. RTDL's
exact scalar route returns the author-reference value for the candidate. Since
the values differ, this candidate cannot support a Figure 5 performance ratio.
```

## Claim Boundary

Allowed:

```text
Goal5289 proves that the current Dragon->Asian scaled Level-B candidate can be
run on the same POD under author and RTDL entrypoints, but it is not value
matched for author X-HD/LB=256 vs RTDL exact route.
```

Not authorized:

```text
Figure 5 reproduced
RTDL/author Figure 5 speedup
same-denominator performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Evidence

Remote artifact:

```text
/tmp/xhd_goal5289_figure5_bounded_probe/xhd_goal5289_figure5_bounded_same_pod_probe.json
```

Local copy:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5289_figure5_bounded_same_pod_probe_2026-07-09.json
```

Focused regression:

```text
tests/goal5289_xhd_figure5_bounded_same_pod_probe_test.py
```

## Next Recommended Step

Do not use this Level-B Dragon->Asian scaled candidate for Figure 5 performance
claims.

Next choices:

```text
1. Find a Figure 5 candidate whose author X-HD/LB=256 path is value-matched on
   the same POD before measuring performance; or
2. Use exact author inputs if they become available; or
3. Move to a figure/blocker where the current public candidate is
   correctness-clean under the paper setting.
```
