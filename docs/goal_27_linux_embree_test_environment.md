# Goal 27: Linux Embree Test Environment Preparation

Date: 2026-04-02

## Goal

Prepare a usable Linux host for RTDL Embree backend testing, verify that Embree works natively on that host, and confirm that the RTDL repository can run its local Embree-side preparation path there.

Target host:

- `192.168.1.20`

## Why This Goal Matters

The local Mac remains the primary development machine, but RTDL also needs a non-macOS Embree environment for backend testing and future validation work. A Linux `x86_64` Embree host gives the project:

- a second CPU/Embree platform
- a more conventional Linux deployment target
- a place to validate native Embree code outside the macOS environment

## Starting State

When the host was first checked, it was reachable over the network and SSH was available, but the machine was not yet ready for RTDL Embree work.

Initial findings:

- Ubuntu 24.04.4 LTS
- `x86_64`
- compiler basics already present:
  - `gcc`
  - `g++`
  - `make`
  - `python3`
  - `pkg-config`
- missing:
  - `cmake`
  - `pip3`
  - Embree development/runtime packages

## Work Performed

### 1. Installed required packages

Installed:

```sh
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  cmake python3-pip libembree-dev embree-tools git
```

### 2. Verified Embree installation

Confirmed:

- header: `/usr/include/embree4/rtcore.h`
- library: `/usr/lib/x86_64-linux-gnu/libembree4.so`

### 3. Verified native Embree usage

Two levels of verification were completed:

- minimal smoke program:
  - create/release an Embree device
- stronger repository validation program:
  - [embree_remote_validation.cpp](/Users/rl2025/rtdl_python_only/apps/embree_remote_validation.cpp)
  - builds a one-triangle scene
  - casts a ray
  - checks:
    - `geomID == 0`
    - `primID == 0`
    - `tfar == 1.0`
    - `u == 0.25`
    - `v == 0.25`

Observed validation output:

```text
embree_validation_ok geomID=0 primID=0 tfar=1 u=0.25 v=0.25
```

### 4. Prepared RTDL workspace on the host

Created and updated:

```sh
~/work/rtdl_python_only
```

The repository was cloned and synchronized to `main`.

### 5. Verified RTDL local build path

Ran:

```sh
make build
```

Result:

- passed on `192.168.1.20`
- RTDL plan lowering succeeded on the Linux host

## Important Caveat

Ubuntu's Embree packaging on this machine does not provide a working:

```sh
pkg-config --modversion embree4
```

So code that assumes `pkg-config --cflags --libs embree4` will work automatically may need a host-specific adjustment. Direct compile/link using the installed headers and `-lembree4` works correctly.

## Review

The native validation program and the updated host report were reviewed by Claude, revised once to align report claims with actual assertions, and then approved.

Saved review note:

- [2026-04-02-claude-review-host-192-168-1-20-embree.md](/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-02-claude-review-host-192-168-1-20-embree.md)

## Deliverables

- environment report:
  - [host_192_168_1_20_embree_enablement_2026-04-02.md](/Users/rl2025/rtdl_python_only/docs/reports/host_192_168_1_20_embree_enablement_2026-04-02.md)
- native validation program:
  - [embree_remote_validation.cpp](/Users/rl2025/rtdl_python_only/apps/embree_remote_validation.cpp)

## Final Result

Goal 27 is complete.

`192.168.1.20` is now a usable Linux `x86_64` Embree test environment for RTDL backend work. It is not an OptiX/NVIDIA machine, but it is ready for CPU/Embree testing and validation.
