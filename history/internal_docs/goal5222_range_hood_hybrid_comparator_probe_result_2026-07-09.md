# Goal5222 - ModelNet40 `range_hood` Hybrid Comparator Probe Result

Date: 2026-07-09

## Verdict

```text
completed_range_hood_failure_explained_by_author_comparator_regime__paper_branch_hybrid_matches
```

Goal5222 investigated the single failing case from Goal5221:

```text
range_hood_0124.off -> range_hood_0004.off
```

The failure was not caused by the RTDL normalized route. It was caused by using
the current `main` branch author `variant=rt` comparator for a paper-branch log
record whose own repeat payload reports:

```text
Algorithm = Hybrid
```

Running the `origin/paper` author branch with `variant=hybrid` on the same
official public ModelNet40 OFF files, with the paper-log preprocessing and
parameters, exactly reproduces the paper-branch HDResult.

## Evidence Artifacts

Downloaded local artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5222_range_hood_comparator_regime_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5222_range_hood_paper_branch_hybrid_repeat5_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5222_range_hood_paper_branch_build_and_probe_artifacts_2026-07-09.tar.gz
```

The tarball contains the paper-branch configure/build logs, submodule update
log, the current main/rt probe, the paper-branch hybrid probe, and the
combined comparator summary.

## Build Provenance

The existing current author comparator remains:

```text
branch = origin/main
head   = 7bf41c8442d059c94f4178355c6d5a10571d9658
binary = /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
variant = rt
reported Algorithm = XHD
```

Goal5222 built a separate worktree and build directory for the paper branch:

```text
branch = origin/paper
head   = 8c3846866052e1e8755210021f23fac2cbe8c3d6
binary = /tmp/xhd-goal5222_build_paper/bin/hd_exec
variant = hybrid
reported Algorithm = Hybrid
```

The paper-branch build required only toolchain/build-compatibility handling:

- reuse initialized `rply` / `cudaKDTree` submodules;
- point `FindOptiX` at the same OptiX 7.7 headers already used by Goal5112;
- consume `gflags`, `glog`, and `hdr_histogram` through modern vcpkg CMake
  targets;
- pin CUDA host compiler to `g++-11`;
- adjust two `std::atomic` zero initializers to brace initialization;
- avoid nvcc parsing GCC AMX intrinsic headers.

These are classified as `Author+BuildPatch` compatibility steps. They do not
change Hausdorff algorithm semantics.

## Probe Command Shape

The decisive probe used the paper-branch binary:

```text
hd_exec
  -input1 /tmp/xhd-modelnet40/extracted/ModelNet40/range_hood/test/range_hood_0124.off
  -input2 /tmp/xhd-modelnet40/extracted/ModelNet40/range_hood/train/range_hood_0004.off
  -n_dims 3
  -input_type off
  -variant hybrid
  -execution gpu
  -normalize=true
  -n_points_cell 8
  -max_hit 256
  -repeat=5
  -check=false
```

## Comparator Matrix

```text
paper log HDResult                         = 0.46497631072998047

current main / variant=rt / Algorithm=XHD  = 0.466653436422348
main/rt vs paper diff                      = 0.0016771256923675537
main/rt matches paper log                  = false

paper branch / variant=hybrid / Algorithm=Hybrid
                                             = 0.46497631072998047
paper/hybrid vs paper diff                 = 0.0
paper/hybrid matches paper log             = true

RTDL normalized route from Goal5221        = 0.46497629417671404
RTDL vs paper diff                         = 1.655326642424626e-08
RTDL matches paper log                     = true
RTDL matches paper/hybrid                  = true
RTDL matches main/rt                       = false
```

## Interpretation

Goal5221's `range_hood` failure is a comparator-regime mismatch:

```text
paper log uses Hybrid
current main/rt reports XHD and differs
paper-branch variant=hybrid matches the paper log exactly
RTDL normalized route matches the paper log and paper-branch Hybrid
```

Therefore the correct interpretation of Goal5221 is:

```text
20/20 ModelNet40 selected cases have an RTDL normalized route matching the
paper-log scalar within tolerance.

19/20 cases also match the current main/rt author comparator.

The remaining case requires the paper-branch Hybrid comparator, which matches
the paper log exactly.
```

This strengthens the ModelNet40 normalized-public-OFF reconstruction candidate.
It does **not** by itself prove all-pair ModelNet40 reproduction, exact dataset
byte identity, or performance parity.

## Claim Boundary

Allowed:

```text
For the selected `range_hood` case, the paper-branch Hybrid author comparator
reproduces the paper log exactly, and RTDL's normalized route matches both
paper log and paper-branch Hybrid within tolerance.
```

Forbidden:

```text
All ModelNet40 pairs are complete.
All paper logs can use current main/rt as the comparator.
Current main/rt is the valid paper comparator for Hybrid paper-log records.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next ModelNet40 goal should update the batch runner / status report so that
paper-log records are compared against the correct author branch and variant:

```text
Algorithm=XHD    -> current main/rt comparator may be valid
Algorithm=Hybrid -> paper branch / variant=hybrid comparator is required
```

Then rerun or reclassify the 20-case batch under algorithm-aware comparator
selection. No broader ModelNet40 claim should be made before that gate.
