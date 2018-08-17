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

cmake_minimum_required(VERSION 3.0)

project(wcsp CXX)

INCLUDE_DIRECTORIES(/Library/gurobi752/mac64/include)
LINK_DIRECTORIES(/Library/gurobi752/mac64/lib)
INCLUDE_DIRECTORIES(/usr/local/Cellar/openblas/0.3.2/include)
LINK_DIRECTORIES(/usr/local/Cellar/openblas/0.3.2/lib)

# set default compilation directory
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/lib")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/bin")

add_subdirectory(src)
