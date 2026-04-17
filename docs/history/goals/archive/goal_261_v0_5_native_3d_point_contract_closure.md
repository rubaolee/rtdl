# Goal 261: v0.5 Native 3D Point Contract Closure

## Purpose

Close the next honesty gap on the `v0.5` line.

Now that the repo has first-class 3D point public types and Python-reference
support, the native CPU/oracle and accelerated backend paths must fail
explicitly instead of silently degrading 3D point inputs into 2D behavior.
