# Goal 269: v0.5 cuNSearch Adapter Skeleton

Date: 2026-04-12
Status: proposed

## Purpose

Add the first concrete external baseline adapter skeleton for the prioritized
RTNN comparison library, `cuNSearch`.

## Why This Goal Matters

Goals 266 and 267 already established:

- `cuNSearch` is the first external adapter priority
- the reproduction matrix expects fixed-radius rows to pair with it

Without a real adapter skeleton, those decisions remain only planning text.

## Scope

This goal will:

1. add a dedicated `cuNSearch` adapter module
2. make Linux binary resolution explicit through environment/config helpers
3. add an invocation-plan object for fixed-radius nearest-neighbor requests
4. add a request-writer that emits a concrete JSON request contract
5. fail honestly when the binary is not configured

## Non-Goals

This goal does not:

- execute `cuNSearch`
- claim any third-party adapter is online
- claim row parity with RTDL

## Done When

This goal is done when the repo has a real, test-covered, bounded adapter
surface for `cuNSearch` that can:

- resolve a configured binary path
- produce an invocation plan
- write an explicit request payload
- fail honestly when the binary is absent
