# Goal5842 pre-worker-zero repair 02

## Incident

The second Ada transaction root was created on the supplied pod at
`/workspace/goal5842-ada-9b4ac6781-transaction02`.  Stage
`00_bind_execution_authority` passed and bound the clean source commit,
virtual-environment launcher, native DSO, Direct binary, PyOptiX/CuPy stack,
and Ada GPU.  Stage `01_gpu_identity_witness_no_timing` then failed while
preparing the sphere task because the legacy native loader could not find
`librtdl_optix`.

The create-only failure marker states:

```text
failed_stage=01_gpu_identity_witness_no_timing
worker_zero_reached=false
new_transaction_after_repair_permitted=true
```

No performance clock is present in the witness.  No causal or baseline worker
started.  Deterministic control flow completed the relation and triangle
CHECK_ON/CHECK_OFF executions before reaching the failing sphere prepare, so
the failed witness made exactly four complete, untimed GPU execution calls.

## Root cause

Goal5842 passed and hashed `--native`, but the existing prepared runtime still
finds its shared library through `RTDL_OPTIX_LIB`.  The Goal5842 entrypoints did
not force that legacy loader variable to the already authorized DSO.  Supplying
an ambient variable in the shell would make the run proceed, but would leave a
real identity gap: the authority could bind one DSO while the runtime loaded
another.

## Repair

The experiment runtime now has one helper that first checks the supplied path
against `execution_authority.execution_paths.native_library`, then overwrites
both legacy loader variables with that resolved authorized path.  The no-timing
witness and the checked RTDL baseline call this helper before prepare.  The
PyOptiX baseline remains independent of RTDL's loader variables.

A regression test proves that an untrusted ambient path is replaced by the
authority-bound path and that both formal GPU entrypoints call the helper.

The successful replacement transaction must repeat the complete six-call
identity witness before any registered timing.  Consequently its timed phase
still begins after the same declared full witness boundary; the four prior
untimed calls are disclosed rather than relabelled as observations.

## Supersession and claim boundary

The v2 preregistration remains byte-preserved at internal seal
`d00d569d11b9eea22a0762cb4c8b93e3e1cc156aff7b5eafa51b7619b42d986d`
and whole-file SHA-256
`12d2acc7f26632e72552e588254ce319669044571eb6b32866737a9a9c31df6c`.
A v3 preregistration must append-only supersede it because formal source bytes
changed.  The task set, inputs, schedules, phase boundaries, statistics,
failure policy, hardware gate, and claim ceiling do not change.

This remains an engineering pre-worker-zero failure, not a scientific failure
or a performance result.  The failed transaction remains preserved on the
pod; no failed row has been dropped or retried.
