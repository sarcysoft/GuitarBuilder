cmake_minimum_required(VERSION 3.20)
project(guitar_builder LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Default to Release if not specified
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose the build type" FORCE)
endif()

# Enable exceptions (needed for Manifold)
set(GODOT_DISABLE_EXCEPTIONS OFF CACHE BOOL "Disable exceptions in godot-cpp" FORCE)
if(MSVC)
    add_compile_options(/EHsc /utf-8 /MP)
endif()

# Output directory for the compiled GDExtension library
set(EXTENSION_OUTPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/project/bin")
file(MAKE_DIRECTORY "${EXTENSION_OUTPUT_DIR}")

# 1. Add godot-cpp
add_subdirectory(thirdparty/godot-cpp)

# 2. Add Manifold (disable tests and extra bindings)
set(MANIFOLD_TEST OFF CACHE BOOL "Build Manifold tests" FORCE)
set(MANIFOLD_PYBIND OFF CACHE BOOL "Build Manifold python bindings" FORCE)
set(MANIFOLD_CBIND OFF CACHE BOOL "Build Manifold C bindings" FORCE)
set(MANIFOLD_DOWNLOADS ON CACHE BOOL "Allow downloading dependencies" FORCE)
set(MANIFOLD_CROSS_SECTION ON CACHE BOOL "Enable 2D CrossSection support" FORCE)

add_subdirectory(thirdparty/manifold)

# 3. GuitarBuilder GDExtension shared library
file(GLOB_RECURSE SRC_FILES 
    "src/*.cpp" 
    "src/*.h"
)

add_library(${PROJECT_NAME} SHARED ${SRC_FILES})

# Link against godot-cpp and manifold
target_link_libraries(${PROJECT_NAME} PRIVATE 
    godot::cpp 
    manifold
)

target_include_directories(${PROJECT_NAME} PRIVATE 
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
    "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/manifold/include"
)

# Automatically copy manifold.dll to the extension directory after building
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    "$<TARGET_FILE:manifold>"
    "${EXTENSION_OUTPUT_DIR}"
)

# Set library output names and ensure output goes directly to project/bin/
if(WIN32)
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_NAME "guitar_builder.windows.$<LOWER_CASE:$<CONFIG>>.x86_64"
        RUNTIME_OUTPUT_DIRECTORY "${EXTENSION_OUTPUT_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${EXTENSION_OUTPUT_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_DEBUG "${EXTENSION_OUTPUT_DIR}"
        PDB_OUTPUT_DIRECTORY "${EXTENSION_OUTPUT_DIR}"
        PDB_OUTPUT_DIRECTORY_RELEASE "${EXTENSION_OUTPUT_DIR}"
        PDB_OUTPUT_DIRECTORY_DEBUG "${EXTENSION_OUTPUT_DIR}"
        PREFIX ""
    )
elseif(UNIX AND NOT APPLE)
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_NAME "guitar_builder.linux.$<LOWER_CASE:$<CONFIG>>.x86_64"
        LIBRARY_OUTPUT_DIRECTORY "${EXTENSION_OUTPUT_DIR}"
        LIBRARY_OUTPUT_DIRECTORY_RELEASE "${EXTENSION_OUTPUT_DIR}"
        LIBRARY_OUTPUT_DIRECTORY_DEBUG "${EXTENSION_OUTPUT_DIR}"
        PREFIX ""
    )
endif()
