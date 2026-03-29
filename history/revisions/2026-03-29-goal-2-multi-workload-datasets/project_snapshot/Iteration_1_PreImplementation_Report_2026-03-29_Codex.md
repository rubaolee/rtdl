# Iteration 1 Pre-Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-2-multi-workload-datasets
Status: awaiting Gemini scope/review-plan feedback

## Proposed Goal

Extend RTDL from one workload to at least three RayJoin workload surfaces, and build a Python dataset pipeline for selected RayJoin datasets so those workloads can be validated before GPU runtime integration.

## Tentative Scope

- LSI
- PIP
- overlay-oriented composition/preparation surface

with RayJoin-aligned datasets starting from the public sample data in the RayJoin repository and then one larger public dataset pair if practical.

## Why This Is A Pre-GPU Goal

This work is mostly about:

- source-language growth,
- IR growth,
- lowering growth,
- dataset parsing and normalization,
- and CPU-side semantic validation.

It does not require an NVIDIA runtime to be useful.

## What I Need From Gemini

I am not asking Gemini to review the implementation yet. I am asking Gemini to help establish consensus on:

1. whether this is the right next goal,
2. which exact workloads and datasets should be in scope,
3. what implementation evidence Gemini will require later before it considers the goal reviewed and done.

The review standard itself needs to be agreed in advance.
