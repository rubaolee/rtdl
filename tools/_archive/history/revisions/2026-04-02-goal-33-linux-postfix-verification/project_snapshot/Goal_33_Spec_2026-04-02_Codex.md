# Goal 33 Spec

Date: 2026-04-02

## Goal

Verify on `192.168.1.20` that the Goal 31 correctness fix and Goal 32 sort-sweep optimization for local `lsi` also hold on the Linux Embree host.

## Scope

- pull the current main branch on the Linux host
- rebuild the native backend there
- run Goal 31 / Goal 32 regression coverage there
- rerun the previously failing exact-source larger slices
- record whether Linux `lsi` parity is restored on `1x5`, `1x6`, and `1x8`

## Fallback Review Rule

Claude is unavailable in this environment, so this round closes under the user-approved Gemini-only fallback.
