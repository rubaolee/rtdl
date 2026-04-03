BUILD_DIR := build

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
OPTIX_LIB_NAME   := librtdl_optix.dylib
VULKAN_LIB_NAME  := librtdl_vulkan.dylib
else
OPTIX_LIB_NAME   := librtdl_optix.so
VULKAN_LIB_NAME  := librtdl_vulkan.so
endif

OPTIX_PREFIX ?= /opt/optix
ifneq ("$(wildcard /usr/local/cuda)","")
CUDA_PREFIX ?= /usr/local/cuda
else ifneq ("$(wildcard /usr/lib/cuda)","")
CUDA_PREFIX ?= /usr/lib/cuda
else
CUDA_PREFIX ?= /usr/local/cuda
endif

OPTIX_INCLUDE := $(OPTIX_PREFIX)/include
CUDA_INCLUDE := $(CUDA_PREFIX)/include
ifneq ("$(wildcard /usr/include/x86_64-linux-gnu)","")
CUDA_SYSTEM_INCLUDE := /usr/include/x86_64-linux-gnu
else
CUDA_SYSTEM_INCLUDE :=
endif
ifneq ("$(wildcard $(CUDA_PREFIX)/lib64)","")
CUDA_LIB := $(CUDA_PREFIX)/lib64
else
CUDA_LIB := /usr/lib/x86_64-linux-gnu
endif

ifneq ("$(wildcard $(CUDA_PREFIX)/bin/nvcc)","")
NVCC ?= $(CUDA_PREFIX)/bin/nvcc
else
NVCC ?= /usr/bin/nvcc
endif
CXX_OPTIX ?= $(NVCC)
GEOS_CFLAGS := $(shell pkg-config --cflags geos 2>/dev/null)
GEOS_LIBS := $(shell pkg-config --libs geos 2>/dev/null)

OPTIX_CXXFLAGS := \
	-std=c++17 -O3 -shared \
	-I$(OPTIX_INCLUDE) \
	-I$(CUDA_INCLUDE) \
	$(GEOS_CFLAGS) \
	-DRTDL_OPTIX_INCLUDE_DIR=\"$(OPTIX_INCLUDE)\" \
	-DRTDL_CUDA_INCLUDE_DIR=\"$(CUDA_INCLUDE)\" \
	-DRTDL_CUDA_SYSTEM_INCLUDE_DIR=\"$(CUDA_SYSTEM_INCLUDE)\" \
	-Xcompiler -fPIC

OPTIX_LDFLAGS := -L$(CUDA_LIB) -lcuda -lnvrtc $(GEOS_LIBS)

# ── Vulkan backend build configuration ────────────────────────────────────────
# Requires: Vulkan SDK (vulkan/vulkan.h), shaderc (shaderc/shaderc.h)
# Set VULKAN_SDK to your Vulkan SDK root, or ensure headers/libs are on system paths.
#
# Example (Linux with LunarG SDK):
#   export VULKAN_SDK=/path/to/VulkanSDK/1.3.xxx/x86_64
#   make build-vulkan
#
VULKAN_SDK      ?= /usr
VULKAN_INCLUDE  := $(VULKAN_SDK)/include
VULKAN_LIB_DIR  := $(VULKAN_SDK)/lib

ifneq ("$(wildcard $(VULKAN_SDK)/lib/libshaderc.so)","")
SHADERC_LINK := -lshaderc
else ifneq ("$(wildcard $(VULKAN_SDK)/lib64/libshaderc.so)","")
SHADERC_LINK := -lshaderc
VULKAN_LIB_DIR := $(VULKAN_SDK)/lib64
else ifneq ("$(wildcard $(VULKAN_SDK)/lib/libshaderc_combined.a)","")
SHADERC_LINK := -lshaderc_combined
else
SHADERC_LINK := -lshaderc
endif

CXX_VULKAN ?= g++

VULKAN_CXXFLAGS := \
	-std=c++17 -O3 -shared -fPIC \
	-I$(VULKAN_INCLUDE) \
	-DRTDL_VULKAN_INCLUDE_DIR=\"$(VULKAN_INCLUDE)\"

VULKAN_LDFLAGS := -L$(VULKAN_LIB_DIR) -lvulkan $(SHADERC_LINK)

.PHONY: build build-optix build-vulkan run run-rtdsl-py run-rtdsl-sim run-rtdsl-embree run-rtdsl-baseline bench-rtdsl-baseline eval-rtdsl-embree eval-section-5-6 eval-section-5-6-publish-2026-03-31 report-rtdsl-paper report-goal14-section-5-6-estimate run-goal15-compare run-goal18-compare run-goal19-compare run-goal23-reproduction test verify clean

build-vulkan:
	mkdir -p $(BUILD_DIR)
	$(CXX_VULKAN) $(VULKAN_CXXFLAGS) \
		src/native/rtdl_vulkan.cpp \
		$(VULKAN_LDFLAGS) \
		-o $(BUILD_DIR)/$(VULKAN_LIB_NAME)

build-optix:
	mkdir -p $(BUILD_DIR)
	$(CXX_OPTIX) $(OPTIX_CXXFLAGS) \
		src/native/rtdl_optix.cpp \
		$(OPTIX_LDFLAGS) \
		-o $(BUILD_DIR)/$(OPTIX_LIB_NAME)

build:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 -c "import rtdsl as rt; from examples.rtdl_language_reference import LANGUAGE_REFERENCE_KERNELS; from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference; from examples.rtdl_goal10_reference import GOAL10_KERNELS; [rt.lower_to_execution_plan(rt.compile_kernel(kernel)) for kernel in (LANGUAGE_REFERENCE_KERNELS + (ray_triangle_hitcount_reference,) + GOAL10_KERNELS)]"

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

eval-section-5-6-publish-2026-03-31:
	PYTHONPATH=src:. python3 -m rtdsl.section_5_6_scalability --build-polygons 100000 --probe-series 100000,200000,300000,400000,500000 --iterations 5 --warmup 1 --workloads lsi --publish-docs

report-rtdsl-paper:
	python3 scripts/generate_embree_paper_report.py

report-goal14-section-5-6-estimate:
	python3 scripts/generate_goal14_section56_estimation.py

run-goal15-compare:
	PYTHONPATH=src:. python3 scripts/goal15_compare_embree.py

run-goal18-compare:
	PYTHONPATH=src:. python3 scripts/goal18_compare_result_modes.py

run-goal19-compare:
	PYTHONPATH=src:.:scripts python3 scripts/goal19_compare_embree_performance.py

run-goal23-reproduction:
	PYTHONPATH=src:. python3 scripts/goal23_generate_bounded_reproduction.py

test:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'

verify:
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=src:. python3 scripts/run_full_verification.py

clean:
	rm -rf $(BUILD_DIR) generated
