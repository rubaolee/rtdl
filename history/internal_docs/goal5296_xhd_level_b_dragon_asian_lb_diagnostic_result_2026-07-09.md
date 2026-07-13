# Goal5296 - X-HD Level-B Dragon -> AsianDragon Load-Balance Diagnostic

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5292 showed that the author Figure 7 `lb_comparison` matrix is absent, and
Goal5295 showed that the current POD lacks `/local/storage/shared/HDDatasets`,
so the exact Figure 7 author matrix cannot be regenerated on this POD.

Goal5296 uses the partial temporary Dragon / AsianDragon inputs that are
currently available on the POD to run a **separately named Level-B author-only
diagnostic**:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
lb values = 0 and 256
```

This goal does not run RTDL, does not regenerate the full author Figure 7
matrix, and does not claim Figure 7 reproduction.

## POD / Author Environment

POD access used only the project wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 ...
```

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Author command shape:

```text
hd_exec -input1 dragon.ply -input2 asian_dragon.ply \
  -input_type ply -n_dims 3 -serialize /tmp/xhd_goal5296/ser \
  -variant rt -execution gpu -repeat 1 -json <out> \
  -check=true -normalize=false -lb=<0|256> -profiling
```

## Results

### `lb=0`

```text
HDResult = 52.453487396240234
Running.AvgTime = 107.254 ms
process wall = 16.25388788431883 s
LargeCells = 0
WL Heavy Peak = 0
iteration 3 ComparedPoints = 7,969,408,615
iteration 3 RTTime = 96.854 ms
iteration 3 CUDATime = 0.054 ms
```

### `lb=256`

```text
HDResult = 52.453487396240234
Running.AvgTime = 131.841 ms
process wall = 17.09253077954054 s
LargeCells = 5060
WL Heavy Peak = 217,071,920
iteration 3 ComparedPoints = 1,242,037,623
iteration 3 RTTime = 45.519 ms
iteration 3 CUDATime = 75.923 ms
iteration 3 OffloadingSize = 27,133,990
```

## Interpretation

The author values match exactly:

```text
lb0 HDResult = lb256 HDResult
abs_diff = 0
```

On this temporary Dragon -> AsianDragon input, `lb=256` reduces iteration-3
compared points and RTTime, but introduces heavy offload work and much larger
CUDATime. The single-run author internal `Running.AvgTime` is slower:

```text
lb256 / lb0 Running.AvgTime = 1.22923642754671
lb256 / lb0 process wall    = 1.0515952298044044
```

This is an author-side diagnostic, not a performance conclusion for RTDL and
not a Figure 7 result.

## Claim Boundary

Allowed:

```text
The current POD can run author hd_exec for lb=0 and lb=256 on the temporary
Dragon -> AsianDragon input.
The two author runs return the same HDResult.
On this single diagnostic input, lb=256 is slower by author Running.AvgTime and
process wall despite reducing compared points in iteration 3.
```

Not authorized:

```text
Figure 7 reproduced
full lb_comparison matrix regenerated
exact paper dataset reproduction
partial temporary inputs are paper inputs
RTDL route result
RTDL/author performance ratio
load-balance speedup claim for RTDL
```

## Validation

Local validation:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json
py -m unittest tests.goal5296_xhd_level_b_lb_diagnostic_test
```

## Next Recommended Step

Choose one:

```text
1. Send Goal5296 for strict review as a separately named Level-B author-only
   diagnostic.
2. If exact /local/storage/shared/HDDatasets becomes available, regenerate the
   real author Figure 7 lb_comparison matrix instead.
3. If the owner wants an RTDL comparison on this temporary Dragon/Asian
   diagnostic, authorize a separate Level-B RTDL diagnostic goal and do not
   call it Figure 7 reproduction.
```
