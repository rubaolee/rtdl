BUILD_DIR := build

.PHONY: build run run-rtdsl-py test clean

build:
	mkdir -p $(BUILD_DIR)

run: run-rtdsl-py

run-rtdsl-py:
	PYTHONPATH=src python3 apps/rtdsl_python_demo.py

test:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src python3 -m unittest tests/rtdsl_py_test.py

clean:
	rm -rf $(BUILD_DIR) generated
