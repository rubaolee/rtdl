# Goal 189: Native Engine Reconstruction

## Goal

Reconstruct the native RTDL engines so they are no longer maintained as
single-file monoliths.

## Why

The current native backends are functionally real, but structurally weak:

- `src/native/rtdl_oracle.cpp`
- `src/native/rtdl_embree.cpp`
- `src/native/rtdl_optix.cpp`
- `src/native/rtdl_vulkan.cpp`

They are large, hard to audit, and hard to extend without regression risk.

## Required Outcome

The native engine layer should become easier to audit and evolve while
preserving the existing C ABI and Python runtime contracts.

That means:

1. split backend logic into coherent modules
2. preserve behavior first
3. keep public C ABI entry points stable
4. keep Python runtimes loading the same backend surfaces
5. verify with bounded native/runtime tests after each slice

## Reconstruction Order

1. native oracle
2. Embree
3. OptiX
4. Vulkan

This order is intentional:

- oracle is the smallest and safest pattern-setting slice
- Embree is the strongest CPU backend and a good second pattern
- OptiX and Vulkan are larger GPU/backend monoliths and should follow after
  the smaller slices establish a stable layout

## Allowed Changes

- new headers under `src/native/<backend>/`
- new `.cpp` modules under backend subdirectories
- small runtime/build updates needed to preserve backend loading
- new bounded tests that verify the reconstructed layout still behaves the same

## Disallowed Changes

- semantic redesign of workload behavior during the split
- opportunistic backend feature expansion during reconstruction
- changing the user-facing Python API
- calling the goal closed before each backend slice has bounded verification

## Closure Standard

This goal is only closed when:

- all four native engines are reconstructed out of the current single-file form
- bounded tests pass for each reconstructed slice
- the final docs explain the new layout honestly
- the closure package is reviewed under the normal `2+` AI consensus process
