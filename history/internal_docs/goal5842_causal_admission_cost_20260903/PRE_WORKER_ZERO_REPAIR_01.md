# Goal5842 pre-worker-zero repair 01

## Incident

The first Ada transaction root was created on the supplied pod at
`/workspace/goal5842-ada-3d762985-transaction01`.  Stage
`00_bind_execution_authority` failed before an execution authority, GPU
identity witness, causal worker, baseline worker, or registered timing
observation was produced.

The create-only failure marker states:

```text
failed_stage=00_bind_execution_authority
worker_zero_reached=false
new_transaction_after_repair_permitted=true
```

The root cause was local orchestration code.  The one-generation runner used
`Path(sys.executable).resolve(strict=True)`.  On the pod, the selected virtual
environment launcher was a symlink to `/usr/bin/python3.12`; resolving it
discarded the virtual environment context.  The authority child therefore
could not import the already installed CuPy/PyOptiX stack.

## Repair

The runner now validates and preserves the absolute launcher path without
resolving its symlink.  A regression test constructs an executable base Python
and a `venv/bin/python` symlink, then proves the selected launcher is retained.

Because the runner and test are preregistered source inputs, the former
preregistration is not reused.  A new preregistration, clean source commit,
native build, Direct binary, preflight receipt, and create-only transaction
root are required before another attempt.

## Claim boundary

This was an engineering preflight failure, not a scientific failure or a
timed result.  The failed transaction remains preserved on the pod.  No row is
deleted, replaced, or retried after worker zero because worker zero was never
reached.
