# Goal5064 RT-BarnesHut Current Implementation Report

Date: 2026-07-06

## Purpose

This report records the current RT-BarnesHut paper-reproduction app state after
the bounded same-input POD gate closed. It answers three questions:

1. What exactly has been implemented?
2. Which parts are RTDL generic system capabilities, and which parts are
   RT-BarnesHut paper-app comparator machinery?
3. Did the implementation preserve the principle that RTDL is a general
   language/system, not a custom RT-BarnesHut product?

## Current Status

The app has completed a bounded same-input RT-BarnesHut reproduction against
`AuthorOfficial`.

Main app path:

- `Paper-reproduction-apps/rt-barneshut-paper/`
- `Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json`
- `Paper-reproduction-apps/rt-barneshut-paper/README.md`
- `scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

Primary evidence:

- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/pod_57582_author_optix_payload_gate/pulled/_runs`

Closed bounded same-input result:

```text
Input size: 32768 bodies
Author new vs treelogy: exact match
AuthorOfficial vs RTDL: matched = true
RTDL mismatch_count: 0
RTDL max_rel_error: 2.3653388501211796e-06
RTDL resident kernel min: 1.1904959678649902 ms
Author RT force phase: 5.579 ms
Narrow force-kernel ratio, RTDL / Author: 0.21338877359114364
```

This is a force-kernel phase comparison only. It is not a whole-program
runtime claim and does not reproduce the full Section 5 evaluation matrix from
the paper.

The broader timing envelope is materially different and must travel with the
narrow ratio:

```text
RTDL reported prep + resident kernel envelope:
  tree_prepare_cpu: 138.08046840131283 ms
  tensor_prepare_host_to_device: 149.1980515420437 ms
  extension_compile: 48.508308827877045 ms
  resident_kernel_min: 1.1904959678649902 ms
  total: about 336.98 ms

Author reported preprocessing + execution:
  preprocessing: 14.744 ms
  execution: 85.166 ms
  total: about 99.91 ms

Reported envelope ratio, RTDL / Author: about 3.37x slower
```

The narrow kernel ratio is valid only as a matched force-kernel phase claim.
It must not be quoted as whole-program performance.

The narrow ratio also has a sampling caveat: the numerator is RTDL
`resident_kernel_min`, while the author denominator is the single reported
`rt_core_force` value from that author run. Using RTDL `resident_kernel_mean`
instead gives:

```text
RTDL resident_kernel_mean / Author rt_core_force
  = 1.2389567852020265 / 5.579
  = about 0.2221
```

Future performance gates should report min, mean, and the author-side statistic
explicitly. Migration thresholds in the next design are therefore based on RTDL
mean, not the best min sample.

## What Was Actually Reproduced

The reproduced phase is:

```text
Author prepared state
  -> RTDL consumes the flattened prepared hierarchy
  -> RTDL runs the author-compatible traversal policy
  -> RTDL computes per-body force output
  -> output is compared against author treelogy force output
```

The current app does not yet reproduce the full author pipeline:

```text
raw bodies
  -> author-style bucket tree construction
  -> DFS node ordering
  -> autorope installation
  -> OptiX scene/GPU state preparation
  -> force computation
```

Instead, the app uses the patched author program to dump the prepared state
that the author binary actually used. RTDL then consumes that state.

## Inputs and Outputs of the Current RTDL Route

Current RTDL input:

```text
author_treelogy_prepared_arrays.json
```

The prepared-state file contains:

- sorted body array;
- flattened Barnes-Hut node array;
- node center/mass/half-size fields;
- member offsets and member indices;
- child offsets and child indices;
- author device fields including `nextPrimId` and `autoRopePrimId`;
- ordered primary launch rays;
- force-law and traversal metadata.

Current RTDL output:

```text
rtdl_forces.txt
```

The output is compared to:

```text
author_treelogy_forces.txt
```

The comparison is same-input and same-prepared-state. The comparator is the
patched author binary, not a Python reference.

## Completion Boolean Boundary

Individual sub-gates intentionally report:

```text
paper_reproduction_complete = false
```

because no single sub-gate authorizes the completed claim by itself. The
bounded same-input completion status comes only from:

```text
_runs/completion_audit/summary.json
overall_status = complete
paper_reproduction_complete = true
```

The manifest therefore distinguishes:

```text
paper_reproduction_complete = false
bounded_same_input_reproduction_complete = true
```

This avoids reading a bounded force-kernel result as full Section 5 paper
evaluation completion.

## Root Cause That Was Fixed

The earlier mismatch was not caused by the inverse-square force formula. The
issue was that RTDL had been using a Python-reconstructed tree and recursive
Barnes-Hut opening traversal. That looked algorithmically plausible, but it
was not the exact execution state and traversal policy used by the author
OptiX program.

The author program behaves more like a payload state machine:

```text
current node + current ray/body
if intersection/opening condition is hit:
    accumulate aggregate or leaf contribution
    continue at autoRopePrimId
else:
    if leaf and not self:
        accumulate exact particle contribution
    continue at nextPrimId
```

The fixed route uses:

```text
author binary prepared-state dump
+ author-optix-payload traversal policy
```

This aligned RTDL with the author's actual prepared state and OptiX payload
state machine.

## Generic RTDL/System Capability Used

The current implementation uses generic-looking data and computation shapes:

- flattened aggregate hierarchy;
- device-side point and node arrays;
- member/child offset arrays;
- aggregate-frontier traversal;
- inverse-square scalar/force reduction;
- CUDA-resident kernel execution.

The schema name used by the paper-app dump is intentionally generic:

```text
generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1
```

This is a promising general RTDL capability because it can apply to workloads
other than RT-BarnesHut, such as hierarchical scalar-field queries,
clustered-point aggregate queries, and other tree-based force or influence
computations.

## App-Specific Machinery

The following pieces are paper-app specific and must not be promoted as RTDL
core semantics:

- `AuthorOfficial` checkout/build/patch machinery;
- `RTBH_FORCE_OUT` author force-output hook;
- `RTBH_PREPARED_ARRAYS_OUT` author prepared-state dump hook;
- author `new` vs `treelogy` comparator;
- same-input prepared-state selection;
- `author-optix-payload` exact replay policy;
- phase-boundary review that compares RTDL resident kernel time to the
  author's RT force phase.

These pieces belong under:

```text
Paper-reproduction-apps/rt-barneshut-paper/
```

They are valid for paper reproduction. They are not RTDL public language API.

## Relationship to v2.14.4 Device-Columnar APIs

The v2.14.4 RayJoin work introduced and hardened a device-columnar prepared
pipeline style:

```text
device-column row buffers
device_order_by / lexsort
device-resident carrier
generic row-buffer handoff
```

RT-BarnesHut did not primarily use that path. The reason is workload shape:

- RayJoin is a row/column pipeline:

  ```text
  LSI rows -> sort/group -> point-location columns -> descriptor carrier
  ```

- RT-BarnesHut is a hierarchical traversal workload:

  ```text
  prepared tree + payload state -> aggregate/frontier traversal -> force reduction
  ```

The current RT-BarnesHut route therefore still lives mainly in:

```text
scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py
```

That file is a diagnostic CUDA/Torch-extension route, not a stable public RTDL
API. This is acceptable for closing the bounded paper reproduction, but it is
not the desired long-term system shape.

## Did This Violate the General-System Principle?

No core/public-language violation has been identified.

The implementation did not add public RTDL APIs such as:

```text
rt_barneshut_author_payload()
treelogy_exact_force()
author_autorope_kernel()
```

The author-specific bridge remains in the paper app. The core remains
app-neutral.

However, the line is not fully mature as a general language feature. The
generic hierarchy traversal capability is still hidden in a diagnostic script
and app-owned prepared-array bridge. Therefore:

```text
Principle preserved at core boundary: yes.
General RTDL API completed for this workload class: no.
```

## What Is Not Claimed

This report does not claim:

- full paper Section 5 evaluation reproduction;
- synthetic-10M/25M/50M, dwarf-4M/50M, or lambb-80M reproduction;
- ChaNGa or Treelogy paper-scale baseline reproduction;
- whole-program speedup;
- RTDL raw-body-to-prepared-tree pipeline parity;
- that ordinary users can already write complete RT-BarnesHut using only
  public RTDL hierarchy APIs.

## Current Technical Debt

1. The generic hierarchy traversal shape is not a public RTDL API.
2. `goal2547_barnes_hut_3d_scalar_subtree_kernel.py` still carries system
   behavior that should be extracted if this workload class becomes official.
3. RT-BarnesHut prepared-state construction is not implemented as RTDL.
4. `author-optix-payload` is necessary for exact paper reproduction, but it
   must remain an app-level comparator adapter unless generalized.
5. A non-RT-BarnesHut app has not yet proved the same hierarchy traversal API.

## Conclusion

The current implementation is a successful bounded paper-reproduction app:

```text
Author prepared state -> RTDL force computation -> author force output match
```

It preserves the general-system principle because author-specific comparator
logic stayed in the paper app. But it also exposes the next product task:
RTDL needs a formal, generic hierarchy traversal / aggregate-frontier API so
this capability is no longer hidden inside a paper-app diagnostic script.
