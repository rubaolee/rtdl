# Goal4162 Predicate Border-Assignment Policy Metadata

Date: 2026-06-09

Status: accepted metadata hardening; behavior unchanged.

## Purpose

Goal4159 showed that mixed-predicate fixed-radius component signatures need an explicit generic border-assignment policy. The current predicate direct-status route assigns each predicate-false border point to the lowest predicate-true point id it observes within radius. That is generic, but until now it was implicit in the kernel and metadata.

Goal4162 exposes the policy as an explicit parameter:

- `border_assignment_policy="lowest_predicate_true_point_id_within_radius"`

The public prepared runner and the internal helper both accept the parameter. The only currently accepted value is the existing behavior. Unsupported values fail closed.

## Boundary

This does not solve the Goal4159 road sparse gap and does not promote the route. It simply makes the candidate route's border behavior machine-visible so a future compatible policy can be added and tested without hidden dispatch or app-specific engine logic.

The all-predicate fast path records `border_assignment_policy="not_needed_all_predicate_true"` because no border assignment is performed.
