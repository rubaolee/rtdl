BUILD_DIR := build

.PHONY: build run run-rtdsl-py run-rtdsl-sim run-rtdsl-embree run-rtdsl-baseline bench-rtdsl-baseline eval-rtdsl-embree eval-section-5-6 report-rtdsl-paper report-goal14-section-5-6-estimate run-goal15-compare run-goal18-compare test verify clean

build:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 -c "import rtdsl as rt; from examples.rtdl_language_reference import LANGUAGE_REFERENCE_KERNELS; from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference; from examples.rtdl_goal10_reference import GOAL10_KERNELS; [rt.lower_to_rayjoin(rt.compile_kernel(kernel)) for kernel in (LANGUAGE_REFERENCE_KERNELS + (ray_triangle_hitcount_reference,) + GOAL10_KERNELS)]"

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

eval-rtdsl-embree:
	PYTHONPATH=src:. python3 -m rtdsl.evaluation_report --iterations 3 --warmup 1

eval-section-5-6:
	PYTHONPATH=src:. python3 -m rtdsl.section_5_6_scalability

report-rtdsl-paper:
	python3 scripts/generate_embree_paper_report.py

report-goal14-section-5-6-estimate:
	python3 scripts/generate_goal14_section56_estimation.py

run-goal15-compare:
	PYTHONPATH=src:. python3 scripts/goal15_compare_embree.py

run-goal18-compare:
	PYTHONPATH=src:. python3 scripts/goal18_compare_result_modes.py

test:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'

verify:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 scripts/run_full_verification.py

clean:
	rm -rf $(BUILD_DIR) generated
