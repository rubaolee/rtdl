# Goal5843 Pre-Worker-Zero Repair 02

## Status

`SUPERSEDED_BEFORE_FORMAL_WORKER_ZERO__NO_FORMAL_TIMING_SAMPLE`

The Goal5843 v2 preregistration was committed at
`d5d77b0ad0b1121da12d700af28cefc7535b63f3`. Its preregistration seal was
`a492b381904390c0fd05c607f33a0febfca04673a272f62fb782802b27dd2b1a` and
its source-manifest seal was
`a5d31edd63d6ff0e0fd90cf3bbf22eaa2e4f0ba879675da72efb864ed624dd08`.

No formal transaction root or `WORKER_ZERO.json` was created. No formal
first or steady timing sample was recorded. The v2 preflight directory is
separate from the future formal transaction and is not admissible as timing
evidence.

## Trigger

The v2 timer-free RTDL preflight first executed the bounded-relation control
correctly, then rejected its lifecycle because `provider_execution` was null.
Static and dynamic inspection established that this is the declared runtime
shape, not missing RT execution. The bounded-relation provider lifecycle has
no triangle-specific execution extension. Its public generic execution result
instead exposes a self-digested traversal receipt that recorded two successful
OptiX launches, 8192 ray-generation invocations, the expected relation route,
the exact native DSO hash, and the exact complete-output digest.

## Repair Boundary

Repair 02 does not add a receipt to the runtime and does not alter the frozen
generic core. The Goal5843 worker now selects evidence by task contract:

- triangle requires its provider-specific scalar execution boundary;
- the row-returning relation control requires `provider_execution` to remain
  absent and wraps the generic result's traversal receipt explicitly.

The controller and RTDL-free independent recount both validate the relation
wrapper schema, absence marker, provider lifecycle schema, exact first/steady
execution count, OptiX classification, route identity, native-library hash,
and output digest. Workloads, outputs, arms, schedule, sampling, estimands,
failure policy, native engine, runtime, and claim ceiling remain unchanged.
A new v3 preregistration and clean source commit are mandatory before formal
execution.
