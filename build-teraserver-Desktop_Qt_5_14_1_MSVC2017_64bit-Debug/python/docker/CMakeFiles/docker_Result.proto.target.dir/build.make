# CMAKE generated file: DO NOT EDIT!
# Generated by "NMake Makefiles JOM" Generator, CMake Version 3.17

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE
NULL=nul
!ENDIF
SHELL = cmd.exe

# The CMake executable.
CMAKE_COMMAND = "E:\Program Files (x86)\CMake\bin\cmake.exe"

# The command to remove a file.
RM = "E:\Program Files (x86)\CMake\bin\cmake.exe" -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = E:\Documents\GitHub\opentera\teraserver

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug

# Utility rule file for docker_Result.proto.target.

# Include the progress variables for this target.
include python\docker\CMakeFiles\docker_Result.proto.target.dir\progress.make

python\docker\CMakeFiles\docker_Result.proto.target: E:\Documents\GitHub\opentera\teraserver\python\messages\Result.proto
	cd E:\Documents\GitHub\opentera\teraserver\python\messages
	protoc Result.proto -I. -I/usr/include/google/protobuf/ --python_out E:/Documents/GitHub/opentera/teraserver/python/docker/../messages/python
	cd E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug

docker_Result.proto.target: python\docker\CMakeFiles\docker_Result.proto.target
docker_Result.proto.target: python\docker\CMakeFiles\docker_Result.proto.target.dir\build.make

.PHONY : docker_Result.proto.target

# Rule to build all files generated by this target.
python\docker\CMakeFiles\docker_Result.proto.target.dir\build: docker_Result.proto.target

.PHONY : python\docker\CMakeFiles\docker_Result.proto.target.dir\build

python\docker\CMakeFiles\docker_Result.proto.target.dir\clean:
	cd E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug\python\docker
	$(CMAKE_COMMAND) -P CMakeFiles\docker_Result.proto.target.dir\cmake_clean.cmake
	cd E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug
.PHONY : python\docker\CMakeFiles\docker_Result.proto.target.dir\clean

python\docker\CMakeFiles\docker_Result.proto.target.dir\depend:
	$(CMAKE_COMMAND) -E cmake_depends "NMake Makefiles JOM" E:\Documents\GitHub\opentera\teraserver E:\Documents\GitHub\opentera\teraserver\python\docker E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug\python\docker E:\Documents\GitHub\opentera\build-teraserver-Desktop_Qt_5_14_1_MSVC2017_64bit-Debug\python\docker\CMakeFiles\docker_Result.proto.target.dir\DependInfo.cmake --color=$(COLOR)
.PHONY : python\docker\CMakeFiles\docker_Result.proto.target.dir\depend

