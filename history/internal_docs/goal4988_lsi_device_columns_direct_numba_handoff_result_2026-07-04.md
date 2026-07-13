# Goal4988 LSI Device Columns Direct Numba Handoff Result

## Verdict

`completed_lsi_pair_device_columns_direct_to_numba_projection__partial_device_resident_fix`

## Why This Goal Exists

The owner correctly remembered that RTDL already had DLPack, CUDA array
interface, neutral-buffer, row-buffer, and partner handoff work from earlier
v2.x / v3 / v4 goals.  The defect was not absence of those assets.  The defect
was that the current RayJoin Section 5.7 writer-free binary route still failed
to use them at a real hot boundary:

```text
exact LSI pair-id device columns
-> copy device columns to NumPy pairs
-> upload those pairs back to CUDA
-> run Numba CUDA reprojection
```

That device -> host -> device loop is exactly the kind of boundary the previous
row-buffer / DLPack / CUDA-array-interface work was supposed to avoid.

## What Changed

File changed:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

Test added:

```text
tests/goal4988_lsi_device_columns_direct_numba_handoff_test.py
```

The app now has a direct path:

```text
exact/bounded LSI pair-id device columns
-> device_column_row_buffer_from_native_pair_columns(...)
-> cuda.as_cuda_array(row_buffer.columns["left_id"])
-> cuda.as_cuda_array(row_buffer.columns["right_id"])
-> existing Numba CUDA reprojection kernel
```

The old NumPy copy path remains as fallback for non-device-columnar execution.

## Implementation Details

New producer split:

```text
produce_lsi_exact_device_columns(...)
produce_lsi_bounded_exact_device_columns(...)
```

These return native device-column owners and leave lifetime management to the
caller.  The existing compatibility functions still return NumPy pairs:

```text
run_lsi_exact_device_columns(...)
run_lsi_bounded_exact_device_columns(...)
```

New projection entry:

```text
numeric_xsect_columns_from_pair_device_columns_numba_device(...)
```

This wraps native pair columns in the generic Layer-1 row-buffer contract and
passes them to Numba through CUDA array interface.  It does not import
`rtdsl.rayjoin_overlay`, does not add an RTDL core primitive, and does not add
RayJoin output-chain semantics to the generic carrier.

## Claim Boundary

This goal fixes one real boundary:

```text
LSI pair-id columns no longer need a device -> NumPy -> device loop before
Numba reprojection when --device-columnar and exact/bounded LSI device columns
are enabled.
```

This goal does not prove full device-resident overlay:

```text
projection outputs are still copied to host arrays for downstream stages;
device sort still returns host order/run tables;
point-location face-id device columns are still copied to NumPy;
carrier/group construction is still CPU/Numba;
no author-performance parity claim is authorized.
```

## Summary Metadata Added

The app summary now distinguishes the two cases:

```text
lsi_pair_input_device_resident
lsi_pair_host_to_device_copy_used
lsi_pair_row_buffer_contract
exact_lsi_device_columns_numba_direct_handoff_used
bounded_exact_lsi_numba_direct_handoff_used
exact_lsi_device_columns_downstream_numpy_copy_used
bounded_exact_lsi_downstream_numpy_copy_used
```

For the direct route, these flags are derived from the generic row-buffer object
and metadata, not hard-coded from CLI route selection:

```text
lsi_pair_input_device_resident = row_buffer.device_resident_candidate
lsi_pair_host_to_device_copy_used = row_buffer.materializes_host_rows_for_bridge
```

The POD gate must inspect both the top-level flags and
`lsi_pair_row_buffer_contract`.  A route-selection flag alone is not sufficient
evidence of device residency.

## Local Verification

Commands run on Windows local tree:

```text
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

Result: passed.

```text
$env:PYTHONPATH='src'
py -m unittest tests.goal4988_lsi_device_columns_direct_numba_handoff_test tests.goal4964_exact_lsi_pair_id_device_columns_test tests.goal4972_bounded_exact_lsi_producer_test tests.goal4947_lsi_pair_columns_numba_handoff_test
```

Result:

```text
Ran 14 tests in 0.048s
OK (skipped=1)
```

The skip is the existing CUDA-availability skip in the Numba handoff test on the
local Windows runtime.

## Next Required POD Gate

This needs a POD run before any performance statement:

```text
section57_overlay_columnar_binary.py
  --device-columnar
  --bounded-exact-lsi-device-columns
  --point-location-device-face-columns
  --fast-scaled-point-pack
  --compiled-group
```

Expected validation:

```text
bounded_exact_lsi_numba_direct_handoff_used == true
bounded_exact_lsi_downstream_numpy_copy_used == false
lsi_pair_input_device_resident == true
lsi_pair_host_to_device_copy_used == false
lsi_pair_row_buffer_contract.device_resident_candidate == true
lsi_pair_row_buffer_contract.materializes_host_rows_for_bridge == false
lsi_pair_row_buffer_contract.host_rows_materialized_before_partner_handoff == false
lsi_row_count and downstream descriptor summaries match the previous route
```

Performance interpretation must stay narrow: this only removes the pair-id
round-trip before projection.  It does not close the full RayJoin 5.7
device-resident pipeline gap.

## External Review Amendments Absorbed

Claude approved the implementation but required two tightening changes:

```text
AM1: derive device-resident flags from row-buffer metadata rather than hard-coded
     route claims.
AM2: make the POD gate rely on row-buffer metadata plus structural output
     alignment, because local tests are source-level guards and do not execute
     the CUDA route.
```

Both amendments are now reflected in the implementation and this report.
