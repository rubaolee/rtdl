# Goal5836 A0 owner authorization

Date: 2026-09-01  
Predecessor commit: `92923035a676768a967b2b22d9592c4d712cd0ad`  
Preaction authority SHA-256:
`7e021a874a13454488bf056c44402225bc1deadfc990cf2a8aeb48eaed9c7f40`

Owner instruction received after the preaction was frozen:

> 持续运行，不要停，直到你真的需要一个pod。重要问题严格自审

Fail-closed interpretation:

```text
AUTHORIZE_STAGE_A0_SOURCE_ACQUISITION_AND_HASHING_ONLY
```

This authorization permits acquiring and hashing the exact planned paper,
planned Git commit, complete source-tree identity, license bytes, and fetch
receipts. It does not authorize source-fidelity inspection under A1, input
selection under A2, route materialization under A3, author or RTDL execution,
product/case-study mutation, POD/GPU use, timing, performance inference,
Paper-App promotion, external review, or public claims.

The instruction to continue until a POD is genuinely needed cannot waive the
preaction's requirement that later stages receive separate owner decisions
after their predecessor evidence exists. A0 must close and undergo strict
self-review before any A1 decision is requested.
