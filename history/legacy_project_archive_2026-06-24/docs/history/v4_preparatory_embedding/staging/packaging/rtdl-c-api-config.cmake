# RTDL V3 draft C ABI source-tree CMake package config.
# This file is relocatable inside the source-tree stage or prefix-style stage.

get_filename_component(_RTDL_C_API_PREFIX "${CMAKE_CURRENT_LIST_DIR}/../../.." ABSOLUTE)
set(_RTDL_C_API_INCLUDE_DIR "${_RTDL_C_API_PREFIX}/include")

set(_RTDL_C_API_LIBRARY_CANDIDATES
  "${_RTDL_C_API_PREFIX}/lib/librtdl_c_api.so"
  "${_RTDL_C_API_PREFIX}/lib/librtdl_c_api.dylib"
  "${_RTDL_C_API_PREFIX}/lib/rtdl_c_api.dll"
  "${_RTDL_C_API_PREFIX}/lib/librtdl_c_api.dll"
)

foreach(_RTDL_C_API_CANDIDATE IN LISTS _RTDL_C_API_LIBRARY_CANDIDATES)
  if(EXISTS "${_RTDL_C_API_CANDIDATE}")
    set(_RTDL_C_API_LIBRARY "${_RTDL_C_API_CANDIDATE}")
    break()
  endif()
endforeach()

if(NOT EXISTS "${_RTDL_C_API_INCLUDE_DIR}/rtdl/rtdl.h")
  set(rtdl-c-api_FOUND FALSE)
  set(rtdl-c-api_NOT_FOUND_MESSAGE "RTDL C ABI header not found under ${_RTDL_C_API_INCLUDE_DIR}")
  return()
endif()

if(NOT _RTDL_C_API_LIBRARY)
  set(rtdl-c-api_FOUND FALSE)
  set(rtdl-c-api_NOT_FOUND_MESSAGE "RTDL C ABI shared library not found under ${_RTDL_C_API_PREFIX}/lib")
  return()
endif()

if(NOT TARGET rtdl::c_api)
  add_library(rtdl::c_api SHARED IMPORTED)
  set_target_properties(rtdl::c_api PROPERTIES
    IMPORTED_LOCATION "${_RTDL_C_API_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${_RTDL_C_API_INCLUDE_DIR}"
  )
endif()

set(RTDL_C_API_PREFIX "${_RTDL_C_API_PREFIX}")
set(RTDL_C_API_INCLUDE_DIR "${_RTDL_C_API_INCLUDE_DIR}")
set(RTDL_C_API_LIBRARY "${_RTDL_C_API_LIBRARY}")
