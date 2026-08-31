embed_ptx(
  OUTPUT_TARGET goal5800-owl-residual-ptx
  PTX_LINK_LIBRARIES owl::owl
  SOURCES deviceCode.cu
)

add_executable(goal5800-owl-residual hostCode.cpp)
target_compile_features(goal5800-owl-residual PRIVATE cxx_std_17)
target_link_libraries(goal5800-owl-residual
  PRIVATE goal5800-owl-residual-ptx owl::owl
)
