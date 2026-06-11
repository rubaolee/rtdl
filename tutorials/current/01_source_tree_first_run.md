# Run From The Source Tree

Status: current v2.10 source-tree tutorial.

Goal: run RTDL without learning the whole system first.

## 1. Open The Repository Root

Use the repository root as your working directory.

Linux/macOS:

```bash
cd rtdl_v0_4_release_prep_review
export PYTHONPATH=src:.
```

Windows PowerShell:

```powershell
cd C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review
$env:PYTHONPATH='src;.'
```

## 2. Run Hello World

First run the source-tree doctor:

Linux/macOS:

```bash
python scripts/rtdl_source_tree_doctor.py
```

Windows PowerShell:

```powershell
py -3 scripts\rtdl_source_tree_doctor.py
```

`PASS` on the required checks means the source tree is usable. Optional
warnings only affect native backend or partner examples.

Then run hello world:

Linux/macOS:

```bash
python examples/current/getting_started/rtdl_hello_world.py
```

Windows PowerShell:

```powershell
py -3 examples\current\getting_started\rtdl_hello_world.py
```

You should see a small result proving that Python can import the source tree and
execute an RTDL example.

## 3. Run The Backend Hello World

```bash
python examples/current/getting_started/rtdl_hello_world_backends.py
```

On Windows PowerShell:

```powershell
py -3 examples\current\getting_started\rtdl_hello_world_backends.py
```

The backend example is still a learner program. It helps you see the difference
between the portable CPU path and optional native backends.

## 4. Keep The Mental Model Small

For now, think of an RTDL program as:

```text
make input columns -> call an RTDL primitive -> read result columns
```

The Python program remains ordinary Python. RTDL only owns the primitive call.

## Next

Continue with [Kernel Shape And Backends](02_kernel_shape_and_backends.md).
