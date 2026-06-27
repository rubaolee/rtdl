# Goal 176: Linux GPU Backend Test Plan For The 3D Demo

## Objective

Strengthen the Linux validation surface for the `v0.3` 3D orbiting-star demo on:

1. `optix`
2. `vulkan`

This goal is a correctness-and-regression test goal, not a new rendering goal.

## Why This Goal Exists

Current Linux GPU coverage is real but still too smoke-oriented:

- Goal 169 closed bounded one-frame compare-clean backend validation
- Goal 170 saved small compare-clean demo artifacts

That is enough to prove the surface exists, but not enough to call the Linux
GPU regression surface “thoroughly tested” for this demo line.

## Accepted Scope

- Linux host only:
  - `lestat@192.168.1.20`
- focus on the 3D orbiting-star visual demo line
- keep the RTDL/Python honesty boundary unchanged
- expand test coverage for:
  - compare-backend parity
  - denser frame sizes
  - multi-frame behavior
  - two-light scene summary metadata
  - optional temporal-blend persistence
- run the tests on Linux after backend builds
- save review and result docs

## Out Of Scope

- Windows Embree movie work
- Linux 4K movie generation
- performance claims beyond bounded test timings
- any new backend semantics
- claims that RTDL is a general rendering engine

## Planned Validation Layers

### 1. Local Python Test Expansion

Add focused tests to a new Linux-backend regression module covering:

- Vulkan one-frame compare parity
- Vulkan two-frame compare parity on a denser scene
- OptiX one-frame compare parity
- OptiX two-frame compare parity on a denser scene
- backend summaries preserving:
  - `light_count = 2`
  - `show_light_source`
  - non-zero `temporal_blend_alpha`

### 2. Linux Native Execution

On `lestat@192.168.1.20`:

- `make build-vulkan`
- `make build-optix`
- run the bounded unittest slice
- run one saved medium compare render for each backend

### 3. Saved Evidence

Save:

- test outputs
- one summary artifact for Vulkan
- one summary artifact for OptiX
- review note and consensus

## Success Criteria

- the new Linux backend regression tests exist in the repo
- the focused test slice passes on Linux for both `vulkan` and `optix`
- one bounded saved compare artifact exists for each backend
- external review is saved
- Codex consensus is saved
