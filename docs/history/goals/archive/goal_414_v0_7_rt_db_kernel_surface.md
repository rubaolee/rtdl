# Goal 414: v0.7 RT Database Kernel Surface

## Goal

Define the first RTDL database-kernel surface that users actually write for the
bounded `v0.7` analytical DB workload family.

## Required outcome

- a small first kernel family is named and justified
- each kernel has:
  - input roles
  - bounded semantics
  - expected emitted fields
- the surface is layered on the existing RTDL kernel model instead of creating
  a separate mini-language

## First kernel family

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Review requirement

This goal requires at least 2-AI consensus before closure.
