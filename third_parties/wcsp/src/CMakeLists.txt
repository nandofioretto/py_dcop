# Copyright (c) 2016-2017 Hong Xu

# This file is part of WCSPLift.

# WCSPLift is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# WCSPLift is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with WCSPLift.  If not, see <http://www.gnu.org/licenses/>.

# Use C++ 11 standard
set(CMAKE_CXX_FLAGS "-std=c++11 ${CMAKE_CXX_FLAGS}")

find_package(Boost REQUIRED COMPONENTS graph program_options system timer)
find_package(BLAS REQUIRED)

if(Boost_FOUND)
  include_directories(${Boost_INCLUDE_DIRS})
endif()

if(BLAS_FOUND)
  include_directories(${BLAS_INCLUDE_DIRS})
endif()

# For now, we assume Gurobi is always available
add_definitions(-DHAVE_GUROBI)
set(GUROBI_VERSION "75" CACHE STRING "Gurobi version.")
# You may need to change gurobi_g++5.2 to gurobi_g++4.2 if you are using an older version of gcc.
set(GUROBI_LIBRARIES "gurobi_g++4.2" "gurobi${GUROBI_VERSION}")

set(wcsp_BINSRCS
  LinearProgramSolver.cpp
  LinearProgramSolverGurobi.cpp
  main.cpp)
add_executable(wcsp ${wcsp_BINSRCS})
target_link_libraries(wcsp ${Boost_LIBRARIES} ${BLAS_LIBRARIES} ${GUROBI_LIBRARIES})
set_target_properties(wcsp PROPERTIES
  OUTPUT_NAME wcsp
  LINKER_FLAG "${BLAS_LINKER_FLAGS}")

install(TARGETS wcsp RUNTIME DESTINATION bin)