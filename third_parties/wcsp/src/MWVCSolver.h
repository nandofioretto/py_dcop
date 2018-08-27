/*
  Copyright (c) 2016-2017 Hong Xu

  This file is part of WCSPLift.

  WCSPLift is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  WCSPLift is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with WCSPLift.  If not, see <http://www.gnu.org/licenses/>.
*/

/** \file MWVCSolver.h
 *
 * Defines the base class for all solvers that solve the MWVC problem on a CCG.
 */
#ifndef MWVCSOLVER_H_
#define MWVCSOLVER_H_

#include "ConstraintCompositeGraph.h"

/** The base class for all solvers that solve the MWVC problem on a CCG.
 *
 * \tparam The type of the CCG. It defaults to \p ConstraintCompositeGraph<>.
 */
template <class CCG = ConstraintCompositeGraph<> >
class MWVCSolver
{
public:
    /** \brief Solve the MWVC problem on a given CCG.
     *
     * \param[in] g The graph to solve the MWVC problem on.
     *
     * \param[out] out A map indicating whether each variable is in the MWVC. Note that if \p out is
     * not empty when it is passed in, it will be merged with the existing key-value pairs.
     *
     * \return The total weight of the MWVC.
     */
    virtual double solve(const typename CCG::graph_t& g,
                         typename std::map<typename CCG::variable_id_t, bool>& out,
                         WCSPInstance<> instance) = 0;
};

#endif // MWVCSOLVER_H_
