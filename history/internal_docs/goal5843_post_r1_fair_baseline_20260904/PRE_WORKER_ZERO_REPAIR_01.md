# Goal5843 Pre-Worker-Zero Repair 01

## Status

`SUPERSEDED_BEFORE_FORMAL_WORKER_ZERO__NO_FORMAL_TIMING_SAMPLE`

The first Goal5843 preregistration was committed at
`bc03f357ff1331b6b3edeb58ba33fab19445d258`. Its preregistration seal was
`30857d8f7fe16ab3408c45be0e20123bb5d377400bbf09829ab9a099de0f2b00` and
its source-manifest seal was
`e7d08869792913cd9b9b7a42ea29e95020575de9a0bf9bbb6b533fd3acbfed81`.

No formal transaction root or `WORKER_ZERO.json` was created. No formal
first or steady timing sample was recorded. Therefore this is an ordinary
pre-worker harness repair, not a post-result retry.

## Trigger

A timer-free provider preflight on the RTX A6000 setup completed Direct and
pinned PyOptiX-compatible full-oracle checks. The public RTDL triangle route
also returned the exact scalar `65530`, observed one OptiX launch, and emitted
the expected scalar-only provider boundary. The Goal5843 worker then failed in
its own inspection code before writing a formal receipt.

The worker made two invalid assumptions:

- It looked for `provider_execution` directly in
  `rtdl.generic_family_lifecycle.v1`; the value is correctly nested under
  `provider_receipt`, whose schema is
  `rtdl.v4.public_protocol_lifecycle.v1`.
- It accessed `result.details`, a field of the lower provider-specific result;
  `GenericFamilyExecutionResultV1` intentionally exposes only the public
  output, identities, digest, and traversal receipt.

The lifecycle tree is recursively read-only, so the repaired worker also
accepts `Mapping` rather than requiring mutable `dict` instances and converts
the selected execution boundary into a plain JSON-compatible snapshot.

## Repair Boundary

Repair 01 changes only the Goal5843 experiment worker, its contract/test
surface, and pre-execution documentation. It adds positive and negative tests
for the exact nested schemas, read-only mappings, scalar-only generic result,
and forbidden provider diagnostic leakage.

The three Goal5838 frozen-core files, provider/runtime implementation, native
engine, workloads, output contracts, arms, schedule, sample counts, estimands,
failure policy, and claim ceiling remain unchanged. A new v2 preregistration
and a new clean source commit are mandatory before formal execution.

## Setup Observations Outside Formal Measurement

The initial pod clone was shallow and lacked two historical Git objects needed
by authority tests. Fetching exactly those commits restored the expected
80/80 preflight test pass; no product source changed. The pinned PyOptiX build
reported OptiX API 9.0 and passed context creation. Its optional setup probe
confirmed that this build does not export legacy `optix.init()`; the Goal5843
worker does not call that API.
