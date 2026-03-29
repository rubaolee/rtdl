BUILD_DIR := build

.PHONY: build run run-rtdsl-py run-rtdsl-sim test clean

build:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 apps/rtdsl_python_demo.py >/dev/null

run: run-rtdsl-py

run-rtdsl-py:
	PYTHONPATH=src:. python3 apps/rtdsl_python_demo.py

run-rtdsl-sim:
	PYTHONPATH=src:. python3 examples/rtdl_simulator_demo.py

test:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'

clean:
	rm -rf $(BUILD_DIR) generated
