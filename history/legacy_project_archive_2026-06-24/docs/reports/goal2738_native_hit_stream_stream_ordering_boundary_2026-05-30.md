# Goal2738: Native Hit-Stream Stream-Ordering Boundary

Date: 2026-05-30
Status: accepted as synchronization-boundary hardening

## Purpose

Claude's Goal2735 review identified CUDA stream synchronization between OptiX producer work and Triton consumer work as a high-priority blocker for any future public true-zero-copy wording.

Goal2738 makes the stream-ordering state explicit in the v2.5 hit-stream handoff metadata. The default remains `not_proven`.

## Changes

- Native hit-stream outputs and handoffs now carry `producer_consumer_stream_ordering`.
- Supported states are:
  - `not_proven`
  - `same_stream`
  - `producer_event_waited_by_consumer`
  - `host_synchronized_before_consumer`
- Metadata now exposes:
  - `stream_synchronization_proven`
  - `true_zero_copy_requires_stream_synchronization`
- Invalid stream-ordering states fail closed.

## Boundary

This is not stream-synchronization evidence. It is a contract hardening step so later pod evidence can record the exact producer-to-consumer ordering mechanism instead of hiding it behind pointer equality.

Public true-zero-copy wording remains blocked unless future evidence proves ownership/lifetime, stream ordering, pointer stability, and public wording approval together.
