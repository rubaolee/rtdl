# Goal 273: v0.5 cuNSearch Response Parser

Date: 2026-04-12
Status: proposed

## Purpose

Add the first bounded parser for a cuNSearch fixed-radius result artifact so the
adapter line can consume normalized external rows instead of stopping at request
generation.

## Why This Goal Matters

After Goal 269, the repo could write a request contract for `cuNSearch`, but it
still could not read a response artifact back into RTDL-shaped rows. That left
the adapter side one-sided.

This goal closes the next contract gap by making a bounded offline response
format executable.

## Scope

This goal will:

1. define a bounded fixed-radius response result type
2. add a loader for a cuNSearch JSON row artifact
3. normalize rows into RTDL comparison shape
4. fail honestly on wrong adapter, response format, or workload
5. add focused tests for valid parsing and rejection paths

## Non-Goals

This goal does not:

- execute cuNSearch
- claim third-party binary integration is online
- claim row-parity closure with RTDL

## Done When

This goal is done when the public Python surface can:

- read a bounded cuNSearch fixed-radius response artifact
- produce normalized RTDL-style rows
- reject unsupported response kinds honestly
