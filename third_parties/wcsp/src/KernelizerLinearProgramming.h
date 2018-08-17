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

/** \file KernelizerLinearProgramming.h
 *
 * Defines the kernelization algorithm using linear programming.
 */

#ifndef KERNELIZERLINEARPROGRAMMING_H_
#define KERNELIZERLINEARPROGRAMMING_H_

#include <memory>

#include "Kernelizer.h"

/** The kernelization algorithm using linear programming.
 *
 * Refer to Kernelizer for details of the template parameter.
 */
template <class CCG = ConstraintCompositeGraph<> >
class KernelizerLinearProgramming : public Kernelizer<CCG>
{
private:
    std::unique_ptr<LinearProgramSolver> lps;

public:
    /** \brief Construct a KernelizerLinearProgramming object using a linear program solver.
     *
     * \param[in] lps The linear program solver.
     */
    KernelizerLinearProgramming(LinearProgramSolver* lps)
    {
        this->lps.reset(lps);
    }

    /** \se{Kernelizer::kernelize}
     */
    virtual void kernelize(typename CCG::graph_t& g,
                           std::map<typename CCG::variable_id_t, bool>& out)
    {
        using namespace boost;

        typedef typename CCG::graph_t graph_t;
        typedef typename boost::graph_traits<graph_t>::vertex_descriptor vertex_t;
        typedef typename boost::graph_traits<graph_t>::edge_descriptor edge_t;

        auto vertex_id_map = get(vertex_name, g);
        auto vertex_weight_map = get(vertex_weight, g);

        lps->reset();

        // map vertex object to its variable id in the linear program solver
        std::map<vertex_t, LinearProgramSolver::variable_id_t> vertex_to_id;

        // iterate over all vertices and add them as variables.
        typename graph_traits<graph_t>::vertex_iterator vi, vi_end, next;
        std::tie(vi, vi_end) = vertices(g);
        for (auto it = vi; it != vi_end; ++ it)
            vertex_to_id.insert(
                std::make_pair(*it,
                               lps->addVariable(vertex_weight_map[*it],
                                                LinearProgramSolver::VarType::CONTINUOUS)));

        lps->setObjectiveType(LinearProgramSolver::ObjectiveType::MIN);

        // iterate over all edges and add them as constraints
        typename graph_traits<graph_t>::edge_iterator ei, ei_end;
        std::tie(ei, ei_end) = edges(g);
        for (auto it = ei; it != ei_end; ++ it)
        {
            std::vector<LinearProgramSolver::variable_id_t> x(2);
            x[0] = vertex_to_id[source(*it, g)];
            x[1] = vertex_to_id[target(*it, g)];
            std::vector<double> coeff = {1.0, 1.0};
            lps->addConstraint(x, coeff, 1.0, LinearProgramSolver::ConstraintType::GREATER_EQUAL);
        }

        // solve the LP
        std::vector<double> assignments;
        lps->solve(assignments);

        // reduce the graph
        for (auto it = vi, next = it; it != vi_end; it = next)
        {
            ++ next;
            // 3 possible values of ass: 0, 0.5, 1.
            double ass = assignments.at(vertex_to_id[*it]);

            if (ass < 0.8 && ass > 0.2)  // ass == 0.5, do nothing on it
                continue;

            auto id = vertex_id_map[*it];

            if (ass > 0.8) // ass == 1
            {
                if (id >= 0)
                    out[id] = true;
                clear_vertex(*it, g);
                remove_vertex(*it, g);
            }
            else if (ass < 0.2) // ass == 0
            {
                if (id >= 0)
                    out[id] = false;
                // Note that all neighbors should have an assignment of 1, otherwise the LP solution
                // is infeasible.
                clear_vertex(*it, g);
                remove_vertex(*it, g);
            }
            else // should not reach here
                throw std::string("Unknown kernelization error");
        }
    }
};

#endif // KERNELIZERLINEARPROGRAMMING_H_
