# RTDL V4：从 GitHub 开始接手

更新日期：2026-10-28。本文的必做步骤只使用 GitHub 已有源码，不依赖原开发者的电脑或额外本机文件。先完成 CPU 起步，再阅读实现与建立可选 GPU 环境。

RTDL V4 是一个面向 NVIDIA OptiX 的受限 Python 回调语言原型。应用作者选择算法及其光线/几何编码；前端将回调源码作为数据解析，检查类型、角色、行为和绑定，再由受支持的后端生成或选择目标实现。它不把任意 Python 应用自动转成 RT 算法，也没有对所有输入的端到端正确性保证。

学习时区分三个层次：CPU 侧解析/验证/解释、真实 GPU 功能执行、性能评测。本指南第一阶段只验证前一个层次。

## 1 先取得正确的版本

仓库：[rubaolee/rtdl](https://github.com/rubaolee/rtdl)。它目前是公开仓库，无须导师提供 GitHub 写权限即可 clone 和运行。

**默认 `main` 保留 V3 源码；它的 README 提供本指南入口，但不能直接作为 V4 代码基线。** 本次已核实的 V4 分支是 `codex/cgo-goal5836-handoff`，固定提交是：

```text
354f89bf4b0c7440034464115536f65950267919
```

请在浏览器中保持本指南打开，再在一个新的工作目录执行。指南随默认分支发布；下面固定的较早 V4 提交本身不含这份新增文档，这是预期的版本差异。

```bash
python3.12 --version
git --version
```

需要 Git、CPython 3.12 和网络。没有 `python3.12` 时先安装 Python 3.12。然后执行：

```bash
git clone --depth 1 --single-branch --branch codex/cgo-goal5836-handoff https://github.com/rubaolee/rtdl.git rtdl
cd rtdl
git switch --detach 354f89bf4b0c7440034464115536f65950267919
git rev-parse HEAD
git status --porcelain
```

验收：HEAD 与上面的 40 位值相同，`git status --porcelain` 无输出。若将来分支前移，浅 clone 不含该提交，先执行 `git fetch --depth 1 origin 354f89bf4b0c7440034464115536f65950267919`，再执行 detach 命令。不要用其它分支“差不多”的版本代替。

`--depth 1` 只缩短 Git 历史，不会缩减该提交的源码文件。需要追踪旧实现时，可执行 `git fetch --unshallow origin` 取回该分支祖先；其它分支或测量提交仍须明确 fetch 和核对。这不是下载了所有历史原始实验数据的承诺。

## 2 建立 CPU 环境并确认导入来源

以下使用 macOS/Linux shell。环境放在仓库外，避免污染源码及 GPU 构建的 clean-tree 条件：

```bash
python3.12 -m venv ../rtdl-cpu-venv
. ../rtdl-cpu-venv/bin/activate
python -m pip install 'numpy==2.3.5' 'setuptools==80.9.0' 'wheel==0.45.1'
python -m pip install --no-build-isolation -e .
python -I -c 'import sys, numpy, rtdsl; import rtdsl.v4 as v4; print(sys.version); print(numpy.__version__); print(rtdsl.__file__); print(v4.V4_API_VERSION)'
```

验收：Python 为 3.12.x、NumPy 为 2.3.5、API 为 `4.0.0rc1`，`rtdsl.__file__` 指向刚 clone 的 `rtdl/src/rtdsl/`，不能指向另一个工作区。隔离导入检查成功后再继续。CPU 阶段不需要 CUDA、OptiX、Numba、GPU 或原始论文数据。

## 3 跑通一个真实 V4 程序

从仓库根目录运行：

```bash
python -I examples/current/v4_restricted_callback_quickstart.py
```

应看到：

```text
status = verified_cpu_semantics
first_hit.item_id = 3
first_hit.t = 4.0
user_source_executed_by_python = false
gpu_execution_claimed = false
```

原始输出是 JSON；上述仅列核对字段。bounds 的 lower 为 `[4,-1,-1]`，upper 为 `[6,1,1]`。这一步确实解析、验证并解释受限回调，但没有生成 PTX 或运行 GPU。

接着打开 [该例子的固定版本](https://github.com/rubaolee/rtdl/blob/354f89bf4b0c7440034464115536f65950267919/examples/current/v4_restricted_callback_quickstart.py)，找到 `CALLBACK_SOURCE`、manifest 和各个 role 的 CPU 调用。说明作者写了什么、哪些内容被当作数据解析、哪个值成为结果。

## 4 验证 IR、ABI 和拒绝行为

```bash
python -m unittest tests.goal5750_v4_callback_ir_test tests.goal5751_v4_callback_abi_test -v
```

验收：总计 24 项测试、`OK`、零失败。这里有类型/角色/语法拒绝和 ABI/身份检查。不要把其中测试用的 synthetic proof descriptor 称为真实外部证明。保留完整日志，不能只截图最后一行。

这条 `-m unittest` 命令从仓库根目录运行，不加 `-I`；`tests` 不属于安装的 `rtdsl` 包。导入来源由第 2 步另行核对。

## 5 保存并解释一份自己生成的 IR

先创建一个新的仓库外记录目录，例如 `mkdir ../rtdl-onboarding-evidence`。在仓库根目录运行：

```bash
python - <<'PY' > ../rtdl-onboarding-evidence/first_ir.json
import json
from examples.current.v4_restricted_callback_quickstart import CALLBACK_SOURCE, callback_manifest
from rtdsl.v4 import compile_callback_source
verified = compile_callback_source(CALLBACK_SOURCE, callback_manifest())
print(json.dumps(verified.program.to_dict(), indent=2, sort_keys=True))
PY
```

验收：文件是合法 JSON；能够指出其中的 records、functions、角色和 effect，并把一个作者表达式对应到 IR 节点。保存 commit、Python/依赖版本、quickstart 输出和 24 项测试日志到同一目录。记录目录不要放进当前源码树。

选择第 4 步现有的一项非法程序测试，解释拒绝的输入、检查位置与原因。先使用已有测试学习行为，不要为了“跑通”关闭验证器或修改历史预期。

## 6 按调用链读代码，不从历史目录漫游

以下文件均在固定 GitHub 基线中：

| 阅读顺序 | 路径 | 要回答的问题 |
|---|---|---|
| 1 | `src/rtdsl/v4.py` | 公开入口与 API 版本是什么？ |
| 2 | `v4_callback_frontend.py`、`v4_callback_ir.py`、`v4_callback_interpreter.py`（均在 `src/rtdsl/`） | 源码如何解析、验证、解释？ |
| 3 | `src/rtdsl/v4_callback_abi.py`、`src/rtdsl/v4_typed_physical_schema.py` | 类型、逻辑字段、实际 metadata 列怎样绑定？ |
| 4 | `src/rtdsl/v4_public_builtin_triangle.py` | verify、compile、materialize、prepare、execute 各做什么？ |
| 5 | `src/rtdsl/v4_callback_numba_codegen.py`、`src/rtdsl/v4_triangle_optix_wrapper_codegen.py`、`src/rtdsl/v4_triangle_optix_compiler.py` | 作者 leaf 与编译器 wrapper 怎样进入 PTX/目标组合？ |
| 6 | `src/rtdsl/v4_triangle_prepared_runtime.py`、`src/native/optix/rtdl_optix_api.cpp`、`src/native/optix/rtdl_optix_v4_callback_poc.cpp` | owner、C ABI 和实际 `optixLaunch` 在哪里？ |
| 7 | `src/rtdsl/v4_callback_lifecycle.py`、`src/rtdsl/v4_bounded_relation.py`、`src/rtdsl/v4_triangle_reduction.py` | 闭合 relation/count 家族与可编辑 triangle 入口有什么区别？ |
| 8 | `Paper-reproduction-apps/`、`experiments/v4_paper_apps_pyoptix/`、`case_studies/` | 应用映射、被测路线和拓扑扩展如何组织？ |

基线已有 editable triangle、两列 typed u32 metadata、合法参数互换、四角色 leaf 编译/组合和公开 GPU 测试。本指南只适用于上述固定提交的 API；其它版本的调用方式需要单独核对。

`examples/current/README.md` 和 `getting_started/` 仍混有 V2.14 内容；quickstart docstring 所指 `docs/v4/tutorial.md` 实际不存在。第一轮按本文指名的 V4 文件学习，避免混用不同版本的 API。

## 7 GPU 是后续独立阶段

完成 CPU 阶段后，在 Linux NVIDIA 机器使用独立 GPU 环境。先阅读固定版本的：

- [真实 native 构建器](https://github.com/rubaolee/rtdl/blob/354f89bf4b0c7440034464115536f65950267919/scripts/build_v4_optix_native_snapshot.py)。
- [公开 triangle 作者测试](https://github.com/rubaolee/rtdl/blob/354f89bf4b0c7440034464115536f65950267919/tests/goal5801_g_public_generic_triangle_authoring_test.py)，目标方法为 `test_real_public_lifecycle_matches_independent_cpu_oracle`。

构建需要 Linux、兼容的 NVIDIA driver、CUDA/OptiX SDK、编译器及 GPU Python 依赖。仓库不会附送受 NVIDIA 许可管理的 SDK。使用 clean commit 与仓库外新输出目录；构建器的 `nvidia-smi` 检查要求实际报告一张 GPU。只有 `CUDA_VISIBLE_DEVICES` 不保证满足这个要求。

以下是独立的 GPU 准备配方。本轮没有执行 GPU 构建/测试，不将此配方标为本轮 GPU 验证通过。先在 Linux 主机准备 NVIDIA driver、CUDA Toolkit、OptiX SDK、g++、nm 和 Git，并使用主机实际支持的版本与 compute capability。

在同一份 clean V4 clone 根目录建立 GPU 环境；下列 Python pin 来自保存的功能环境，不是跨版本兼容性承诺：

```bash
python3.12 -m venv ../rtdl-gpu-venv
. ../rtdl-gpu-venv/bin/activate
python -m pip install 'numpy==2.4.4' 'numba==0.65.1' 'llvmlite==0.47.0' 'setuptools==80.9.0' 'wheel==0.45.1'
python -m pip install --no-build-isolation -e .
python -I -c 'import sys, numpy, numba, llvmlite, rtdsl; print(sys.executable); print(numpy.__version__, numba.__version__, llvmlite.__version__); print(rtdsl.__file__)'
```

最小 triangle 测试不要求先安装 PyOptiX 或 CuPy。将以下所有占位路径换成自己的实际路径，`RTDL_GPU_PYTHON` 使用上一条命令打印的解释器路径。示例采用 CUDA 12.8、OptiX 9.0.0、CC 8.9；其它硬件的 CC 要相应修改。

```bash
export RTDL_GPU_PYTHON=/absolute/path/to/rtdl-gpu-venv/bin/python
export RTDL_CUDA_PREFIX=/actual/path/to/cuda-12.8
export RTDL_OPTIX_PREFIX=/actual/path/to/OptiX-SDK-9.0.0
export CUDA_HOME="$RTDL_CUDA_PREFIX"
export PATH="$RTDL_CUDA_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$RTDL_CUDA_PREFIX/lib64:$RTDL_CUDA_PREFIX/nvvm/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader
"$RTDL_CUDA_PREFIX/bin/nvcc" --version
g++ --version
export RTDL_CC=8.9
export RTDL_BUILD=/absolute/path/to/new-rtdl-build
mkdir -p "$RTDL_BUILD"
git status --porcelain
"$RTDL_GPU_PYTHON" scripts/build_v4_optix_native_snapshot.py \
  --cuda-prefix "$RTDL_CUDA_PREFIX" \
  --optix-prefix "$RTDL_OPTIX_PREFIX" \
  --expected-optix-sdk 9.0.0 --compute-capability "$RTDL_CC" \
  --output "$RTDL_BUILD/librtdl_optix.so" \
  --manifest "$RTDL_BUILD/native_manifest.json" \
  --log "$RTDL_BUILD/native_build.log"
export RTDL_GOAL5801_G_NATIVE="$RTDL_BUILD/librtdl_optix.so"
export RTDL_GOAL5801_G_OPTIX_INCLUDE="$RTDL_OPTIX_PREFIX/include"
export RTDL_GOAL5801_G_CUDA_INCLUDE="$RTDL_CUDA_PREFIX/include"
export RTDL_GOAL5801_G_COMPUTE_CAPABILITY="$RTDL_CC"
export RTDL_GOAL5801_G_EVIDENCE_OUTPUT="$RTDL_BUILD/triangle_source_execution.json"
"$RTDL_GPU_PYTHON" -I tests/goal5801_g_public_generic_triangle_authoring_test.py \
  Goal5801GPublicGenericTriangleAuthoringTest.test_real_public_lifecycle_matches_independent_cpu_oracle
```

构建前 `git status --porcelain` 应无输出；构建输出必须是新文件，不能覆盖旧产物或用 `--allow-dirty` 绕过身份条件。验收必须是目标 GPU 方法实际执行、没有 skip，完整小输出与独立 CPU oracle 相同，并保留 `optix_traversal_observed` 等执行记录。缺少环境变量导致的 skip 不算 GPU 通过。应产生 `triangle_source_execution.json` 及三份 PTX；记录的 status 为 `PASS__ORACLE_ISOLATED_REHASHABLE_HOME_EXECUTION`，含三个变体，每个变体的 `traversal_receipt.physical_executor_classification` 为 `optix_traversal_observed`。保存源码 commit、环境、目标和输出；这只是小规模功能测试，不是完整应用或性能评测。

## 8 第一份接手交付与继续开发

第一天提交给导师：

1. `ONBOARDING_RESULT.md`：GitHub URL、branch、完整 commit、OS/Python/依赖、导入路径、所执行命令及退出码。
2. quickstart 完整输出、24 项测试完整日志、`first_ir.json`。
3. 半页说明：应用作者负责算法/RT 编码，编译器额外检查和生成什么，CPU 成功不保证什么；解释一个现有非法程序测试的输入、拒绝位置与原因。
4. 一张自己画的 source→IR→binding/ABI→wrapper/leaf→owner→native launch 调用链；标明尚未实际运行的 GPU 部分。

四项全部完成、且版本核对正确，才算完成 CPU 接手。没有 GPU 或大型数据集不阻塞此阶段。

继续研究前，从固定基线建自己的分支：

```bash
git switch -c codex/phd-onboarding
```

先写一个边界明确的问题及验收条件，再修改实现。先选择一项有明确输入、预期输出和检查方法的小改动。旧结果始终保留原源码身份；修复后的结果使用新提交、新目录和完整输出，不覆盖旧失败。向导师提交 diff/commit 或 PR；写权限由导师按实际协作方式授予，未获得前仍可在自己的 clone 中开发。

## 9 范围与验证环境

本文固定的源码为 GitHub 提交 `354f89bf4b0c7440034464115536f65950267919`。已在 macOS arm64、CPython 3.12.14、NumPy 2.3.5 上，从 GitHub 新 clone 创建独立 venv、editable install，并实际通过：

- 隔离导入来源检查；
- restricted-callback quickstart 的 CPU 语义与完整小结果；
- 24 项 IR/ABI 测试；
- 完整 IR 生成。

运行后 clone 仍为 clean。上述验证不等于任意程序、任意后端、所有输入或不同平台都正确；也不是 GPU 或性能结果。GPU 配方需要在具备对应资源的 Linux 主机另行执行。

保存失败与成功日志，修复使用新提交和新输出。不要通过关闭检查、改阈值或删除不利记录来把失败变成通过。
