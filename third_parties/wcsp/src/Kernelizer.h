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

/** \file Kernelizer.h
 *
 * Define the base class for all classes representing kernelization algorithms.
 */
#ifndef KERNELIZER_H_
#define KERNELIZER_H_

#include "ConstraintCompositeGraph.h"

/** The base class for all classes representing kernelization algorithms.
 *
 * \tparam CCG The Constraint Composite Graph type. It defaults to \p ConstraintCompositeGraph<>.
 */
template <class CCG = ConstraintCompositeGraph<> >
class Kernelizer
{
public:
    /** \brief Kernelize the graph \p g.
     *
     * After calling this function, \p g is kernelized and modified, and \p out contains the
     * variables that are kernelized as well as their values. All child classes of \p Kernelizer
     * must implement this function.
     *
     * \param [in,out] g The graph to kernelize.
     *
     * \param [out] out The variables that are kernelized as well as their values.
     */
    virtual void kernelize(typename CCG::graph_t& g,
                           std::map<typename CCG::variable_id_t, bool>& out) = 0;
};

#endif // KERNELIZER_H_
