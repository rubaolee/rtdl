# Goal 268: v0.5 Bounded Dataset Manifests

Date: 2026-04-12
Status: proposed

## Purpose

Add deterministic bounded dataset manifests for the first RTNN-aligned local
comparison package.

## Why This Goal Matters

The `v0.5` line already has:

- a dataset registry
- a baseline registry
- a reproduction matrix
- a first external adapter skeleton

But it still lacks the concrete bounded dataset manifests that tell later code
exactly what local package each family is supposed to use.

## Scope

This goal will:

1. add a dedicated RTNN bounded-manifest module
2. define one bounded manifest per RTNN dataset family
3. keep deterministic bounded rules explicit
4. add a writer that emits a JSON manifest artifact
5. add focused tests for registry coverage and manifest serialization

## Non-Goals

This goal does not:

- download datasets
- claim exact paper datasets are online
- claim the bounded packages already exist on disk

## Done When

This goal is done when the public Python surface can:

- enumerate bounded dataset manifests
- resolve them by dataset handle
- write a stable JSON manifest artifact for downstream Linux comparison work
