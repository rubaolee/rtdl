# Goal 1570: carry-alias implementation preflight

## Verdict

Design A from Goal 1569 is still the right first carry-copy diagnostic, but the
current kernel surface has a counts-path gap.

The existing pointer-descriptor materialize and mark kernels use uploaded
`first_counts` and `second_counts` arrays. The accepted fastest path uses
`current_counts_device` with derived descriptors. Therefore a carry-alias
diagnostic has two implementation choices:

1. use existing pointer kernels and pay explicit count download/upload cost for
   odd levels;
2. add counts-aware pointer-descriptor kernels that read a device
   `current_counts` array directly.

The first choice is safer for a diagnostic and measures the real cost of using
the existing pointer path. The second choice is a better production candidate
only if the first proves row-copy removal can beat descriptor overhead.

## Current Gap

`launch_parallel_compact_level(...)` currently chooses by counts mode first:

```text
if use_device_level_counts:
    use derived counts kernel
else if use_derived_level_descriptors:
    use derived host-count kernel
else:
    use pointer descriptor host-count kernel
```

So `use_device_level_counts` currently prevents pointer-descriptor materialize
and mark kernels from being selected.

## Diagnostic Plan

Add an opt-in diagnostic flag such as:

```text
RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC=1
```

When all of these are true:

- current merge level has a carry segment;
- `current_rows.size() != 2`;
- batched compact level is active;
- derived descriptors and device counts are active;
- the diagnostic flag is set;

then run that odd level in pointer-descriptor mode by:

- downloading `current_counts_level_device` for the active level;
- building `merge_first_rows`, `merge_second_rows`, `merge_output_rows`;
- building `merge_first_counts`, `merge_second_counts`;
- uploading those descriptor/count arrays;
- keeping the carry count copy into `next_counts_level_device`;
- aliasing the carry row pointer instead of copying row data;
- writing paired outputs into the normal output stage so the next level can
  return to derived descriptors if no aliased carry segment remains.

## Required Measurements

The diagnostic report must separate:

- saved row carry-copy time;
- remaining count-copy time;
- count download/upload cost;
- pointer descriptor upload cost;
- total case timing for `65537`;
- no-carry regression guard for `131072`.

## Guardrails

- Do not enable this path by default.
- Do not use it for the final `current_rows.size() == 2` merge.
- Do not skip the carry count copy.
- Do not claim speedup unless `65537` improves and `131072` does not regress.
- Do not publish public speedup wording from this diagnostic.
