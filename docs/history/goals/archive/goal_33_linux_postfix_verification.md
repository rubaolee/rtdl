# Goal 33 Linux Post-Fix Verification

Date: 2026-04-02

## Goal

Verify on `192.168.1.20` that the Goal 31 correctness fix and Goal 32 sort-sweep optimization for local `lsi` also hold on the Linux Embree host, not only on this Mac.

## Scope

- pull the current main branch on `192.168.1.20`
- rebuild the RTDL Embree backend on that host
- run the Goal 31 / Goal 32 regression tests there
- rerun the previously failing exact-source `County ⊲⊳ Zipcode` larger slices on that host
- record whether the old Goal 28D `1x5`, `1x6`, and `1x8` `lsi` parity failures remain
- close this round under a Gemini-only fallback if Claude remains unavailable/quota-blocked

## Acceptance

- Linux-host unit/regression tests pass for Goal 31 / Goal 32 coverage
- at least the frozen prior failing `1x5` slice is parity-clean on Linux after the fix
- report states clearly whether `1x6` and `1x8` are also parity-clean
- no code changes are required for closure; this is a host verification/report round
