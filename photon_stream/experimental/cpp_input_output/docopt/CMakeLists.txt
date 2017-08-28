cmake_minimum_required(VERSION 3.1)
project(docopt.cpp VERSION 0.6.1)

include(GNUInstallDirs)

#============================================================================
# Internal compiler options
#============================================================================
# C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT CMAKE_CXX_STANDARD OR CMAKE_CXX_STANDARD LESS 11)
	set(CMAKE_CXX_STANDARD 11)
endif()

# Suppression of "unknown pragma" warning on GCC
if(CMAKE_COMPILER_IS_GNUCXX)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-unknown-pragmas") # Code uses #pragma mark
endif()

#============================================================================
# Sources & headers
#============================================================================
set(docopt_SOURCES docopt.cpp)
set(docopt_HEADERS
		docopt.h
		docopt_private.h
		docopt_util.h
		docopt_value.h
		)

#============================================================================
# Compile targets
#============================================================================
add_library(docopt SHARED ${docopt_SOURCES} ${docopt_HEADERS})