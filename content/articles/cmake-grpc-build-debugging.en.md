## A build failure with several causes

A C++ gRPC project failed during configuration because CMake could not find the gRPC package configuration. Once dependency discovery was changed, the build exposed separate problems in Protocol Buffers code generation, generated header paths, and linking a transitive HDF5 dependency. This note reconstructs the sequence from my [original Chinese post](https://blog.csdn.net/ruiqideng/article/details/151805376), published in September 2025, with technical clarifications added in November 2026.

The original record did not include the Linux distribution, package versions, or a complete project. The snippets below illustrate the reported failure and a possible structure; they are not a verified, drop-in reproduction of the original environment.

## Finding gRPC

The project initially requested package configuration files and imported targets:

```cmake
find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf CONFIG REQUIRED)
# Later: target_link_libraries(my_target PRIVATE gRPC::grpc++)
```

Configuration stopped with a message that `gRPCConfig.cmake` or `grpc-config.cmake` could not be found. This means CMake did not find a suitable configuration file in its search locations. It does not by itself prove that gRPC was absent or that every distribution package lacks the file. Before changing the build, check the installed package contents and whether `gRPC_DIR` or `CMAKE_PREFIX_PATH` points to the intended installation.

In the environment described in the original post, I used system-provided `pkg-config` metadata instead of rebuilding the dependency stack. The package names and available flags depend on the distribution:

```cmake
find_package(PkgConfig REQUIRED)
pkg_check_modules(GRPC REQUIRED IMPORTED_TARGET grpc++)
pkg_check_modules(PROTOBUF REQUIRED IMPORTED_TARGET protobuf)
pkg_check_modules(MATIO REQUIRED IMPORTED_TARGET matio)

# Attach these to the target that uses them:
target_link_libraries(my_target PRIVATE
    PkgConfig::GRPC PkgConfig::PROTOBUF PkgConfig::MATIO)
```

The imported-target form is a revision of the original variable-based example. It carries the usage requirements that CMake can obtain from `pkg-config`; inspect the metadata and resulting link command, especially when linking static libraries. See CMake's [FindPkgConfig documentation](https://cmake.org/cmake/help/latest/module/FindPkgConfig.html).

## Restoring code generation

After the switch, configuration reported `Unknown CMake command "protobuf_generate_cpp"`. Finding library metadata with `pkg_check_modules` does not define Protobuf's CMake generation helpers. The original explanation incorrectly implied that Config mode always provides `protobuf_generate_cpp` and `grpc_generate_cpp`. The available commands depend on the package, version, and discovery mode: CMake's [FindProtobuf documentation](https://cmake.org/cmake/help/latest/module/FindProtobuf.html) describes the module-mode helpers and the compatibility conditions for Config mode.

The original solution located `protoc` and `grpc_cpp_plugin`, then made the generated files explicit build outputs. The following is the original approach in abbreviated form; `PROTO_FILE` and the output variables must be defined for the actual project:

```cmake
find_program(PROTOC_EXECUTABLE NAMES protoc REQUIRED)
find_program(GRPC_CPP_PLUGIN NAMES grpc_cpp_plugin REQUIRED)

add_custom_command(
    OUTPUT ${PROTO_SRCS} ${PROTO_HDRS} ${GRPC_SRCS} ${GRPC_HDRS}
    COMMAND ${PROTOC_EXECUTABLE}
        --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
        --cpp_out=${CMAKE_CURRENT_BINARY_DIR}
        --plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}
        -I ${CMAKE_CURRENT_SOURCE_DIR}
        ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
    VERBATIM
)
```

Add the generated sources to a target in the same directory. If the schema imports other `.proto` files, include those dependencies or use an appropriate depfile so changes trigger regeneration. Match the compiler, generated code, plugin, and runtime versions; a successful configure step alone does not establish compatibility. See [add_custom_command](https://cmake.org/cmake/help/latest/command/add_custom_command.html).

## Generated headers and missing symbols

The next failure was a missing generated `.pb.h` header. The files were written under `CMAKE_CURRENT_BINARY_DIR`, but a consumer did not have that directory on its include path. The relevant target needs that path, either directly or through the public interface of the library that owns the generated headers:

```cmake
# Illustrative target names; generated sources must be defined above.
add_library(service_proto ${PROTO_SRCS} ${GRPC_SRCS})
target_include_directories(service_proto PUBLIC
    "${CMAKE_CURRENT_BINARY_DIR}")
target_link_libraries(service_proto PUBLIC
    PkgConfig::GRPC PkgConfig::PROTOBUF)
```

A later `undefined reference` to a generated stub was a link-stage issue: the client used generated declarations but did not link the target containing their compiled implementations. Linking only the system gRPC library was insufficient. The project fixed this by linking the client to its own generated-code library:

```cmake
target_link_libraries(my_client_app PRIVATE service_proto)
```

Missing headers and undefined symbols can have other causes. Check the actual generated output, target membership, link line, symbol names, and ABI before assuming the same diagnosis applies.

## Following the HDF5 dependency

The final recorded linker error was `cannot find -lhdf5`. In that environment the project used `matio`, which depended on HDF5, and the relevant library directory was outside the linker's default search path. The original debugging record inspected `pkg-config --libs matio` and located `libhdf5.so`; its workaround added `MATIO_LIBRARY_DIRS` to the link search path.

A target-scoped imported `PkgConfig::MATIO` is worth trying first, provided the `.pc` files describe the installation correctly. Inspect `pkg-config --libs matio`, `pkg-config --static --libs matio` when appropriate, and the verbose build link line. The `.pc` metadata, development packages, library search paths, and static-versus-shared linkage all matter; an imported target cannot repair incomplete metadata. Use the original workaround only after identifying the missing directory, and avoid assuming one machine's path applies everywhere.

## What the failure taught me

A CMake build is a graph of targets and generated artifacts. Package discovery, code generation, include propagation, and linking are separate steps: fixing one does not validate the others. An imported target can carry include directories, compile options, and link dependencies when its package defines them correctly; neither Config mode nor Module mode guarantees perfect metadata. Choose the mechanism that is supported by the installed packages and inspect what it actually supplies.

For a useful future reproduction, record the operating system, CMake and compiler versions, package origins, `protoc` and plugin versions, exact configure and link commands, and a minimal project. The original environment was not reconstructed for this revision, so the case remains an engineering account rather than a tested recipe.
