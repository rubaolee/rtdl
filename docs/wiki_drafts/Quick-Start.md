# Historical Wiki Draft Note

This page was imported from a parallel checkout on 2026-04-10 as a preserved
draft artifact. It is **not** the current live source of truth for RTDL docs.
For current onboarding, start at [docs/quick_tutorial.md](/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md).

---

# Quick-Start Guide

Getting RTDL running on your local machine is designed to be a "five-minute" process.

## 1. Prerequisites

### macOS (Apple Silicon recommended)
Ensure you have Homebrew installed, then run:
```bash
brew install geos embree
```

### Linux (Ubuntu/Debian)
Install GEOS and a recent Python:
```bash
sudo apt-get update && sudo apt-get install -y libgeos-dev python3.10
```

## 2. Installation

Clone the repository and install the Python dependencies:
```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
python3 -m pip install -r requirements.txt
```

## 3. Your First Run

The fastest way to verify the installation is to run the "Hello World" example. This shots a single ray through a tiny scene and reports a hit.

**Note**: You must prefix commands with `PYTHONPATH=src:.` so that Python can find the local `rtdsl` package.

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
```

Expected output:
```text
hello, world
```

## 4. Testing Backends

If you have native dependencies like Embree or OptiX installed, you can try the backend-aware hello world:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu
PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend embree
```

## Next Steps
Head over to the [Core Concepts](Core-Concepts) page to learn how to write your own kernels.
