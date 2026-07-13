# Goal5349 - X-HD hd_exec Variant Value Surface

## Verdict Label

```text
hd_exec_variant_value_surface_implemented__algorithm_parity_not_claimed
```

## Purpose

The final X-HD objective is "same function except language." One visible
functional mismatch remained in the app-owned `hd_exec` wrapper:

```text
argparse accepted -variant <eb|nn|itk|clover|rt>
but run_rtdl_hd_exec raised ValueError unless variant == rt
```

Goal5349 reduces that option-surface gap.

## Implemented Change

File changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

New behavior:

```text
-variant eb|nn|itk|clover|rt is accepted.
Every variant returns a directed input1->input2 HDResult through the selected
generic RTDL route.
```

The payload now records:

```text
RTDL.variant_support.requested_author_variant
RTDL.variant_support.status
RTDL.variant_support.hdresult_value_supported
RTDL.variant_support.author_variant_algorithm_equivalence_claimed = false
RTDL.variant_support.performance_parity_claimed = false
```

For `variant=rt`:

```text
status = xhd_rt_value_route
```

For `variant=eb|nn|itk|clover`:

```text
status = author_variant_value_compatible_route_only
```

## Boundary

This is **not** author variant algorithm reproduction.

Allowed:

```text
RTDL accepts all author variant names and returns a directed HDResult value.
```

Not authorized:

```text
author eb/nn/itk/clover algorithm equivalence;
author variant timing denominator equivalence;
author performance parity;
Figure 5 baseline reproduction;
full X-HD paper reproduction.
```

## Tests

New:

```text
tests/goal5349_xhd_hd_exec_variant_value_surface_test.py
```

Updated:

```text
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
```

Expected focused validation:

```text
py -m unittest tests.goal5349_xhd_hd_exec_variant_value_surface_test
Ran 3 tests OK

py -m unittest tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test tests.goal5349_xhd_hd_exec_variant_value_surface_test
Ran 9 tests OK
```

## Functional Effect

This improves `hd_exec` option-surface compatibility: users can pass the same
variant names as the author executable and receive a valid directed HDResult
JSON. It does not make those variants algorithmically or performance-equivalent
to the author's C++/CUDA/OptiX implementations.

## Next Step

Send Goal5349 for strict review together with Goal5348 if desired. Future work
for full paper reproduction still needs author variant-specific algorithm and
performance semantics if Figure 5 baseline reproduction is required.
