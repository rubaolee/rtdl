BUILD_DIR := build

.PHONY: build run run-rtdsl-py run-rtdsl-sim run-rtdsl-embree run-rtdsl-baseline bench-rtdsl-baseline test clean

build:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 apps/rtdsl_python_demo.py >/dev/null

run: run-rtdsl-py

run-rtdsl-py:
	PYTHONPATH=src:. python3 apps/rtdsl_python_demo.py

run-rtdsl-sim:
	PYTHONPATH=src:. python3 examples/rtdl_simulator_demo.py

run-rtdsl-embree:
	PYTHONPATH=src:. python3 examples/rtdl_embree_demo.py

run-rtdsl-baseline:
	PYTHONPATH=src:. python3 -m rtdsl.baseline_runner lsi --backend both
	PYTHONPATH=src:. python3 -m rtdsl.baseline_runner pip --backend both
	PYTHONPATH=src:. python3 -m rtdsl.baseline_runner overlay --backend both
	PYTHONPATH=src:. python3 -m rtdsl.baseline_runner ray_tri_hitcount --backend both

bench-rtdsl-baseline:
	PYTHONPATH=src:. python3 -m rtdsl.baseline_benchmark --iterations 3 --warmup 1
	PYTHONPATH=src:. python3 -m rtdsl.baseline_summary build/embree_baseline_benchmark.json

test:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'

clean:
	rm -rf $(BUILD_DIR) generated
