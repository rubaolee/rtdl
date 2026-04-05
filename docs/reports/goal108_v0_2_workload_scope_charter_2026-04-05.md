# Goal 108 RTDL v0.2 Workload Scope Charter

Date: 2026-04-05
Author: Codex
Status: complete

## Purpose

This report turns the accepted Goal 107 roadmap into a concrete workload-scope
charter.

The purpose is to stop v0.2 from becoming diffuse before implementation begins.

## Core decision

The most important decision in this charter is:

- **workload-first**

That means v0.2 will be judged first by whether RTDL closes one additional
coherent workload family beyond the v0.1 RayJoin-centered slice.

## In-scope decision

The charter now keeps only one family in core scope:

1. additional spatial filter/refine workloads

This is the only workload family that currently satisfies all of the needed
conditions strongly enough to define the release:

- coherent with RTDL identity
- realistic on current hardware
- verifiable
- useful for language/runtime growth
- close enough to the proven v0.1 base to justify expansion

## Experimental decision

The charter keeps these as experimental:

- programmable counting/ranking kernels with geometric candidate structure
- generalized ray/path/filter/count kernels
- small graph/geometric counting kernels

This does not mean they are weak ideas. It means they are not stable enough to
define the release yet.

Generate-only mode is no longer treated as a workload family in this charter.
It remains a separate experimental product-mode track governed by the Goal 107
gates.

## Out-of-scope decision

The charter explicitly pushes these out of v0.2 core scope:

- full exact polygon overlay materialization
- distributed or multi-GPU execution
- native AMD backend work without AMD hardware
- native Intel backend work without Intel GPU hardware
- arbitrary AI-generated demo accumulation

## Recommended consequence

The next implementation goal after this charter should be:

- choose the single in-scope family
- define its correctness boundary
- close it end-to-end

That is the point of Goal 110.
