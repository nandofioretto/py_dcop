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

/** \file MWVCSolverLinearProgramming.h
 *
 * Define the MWVC solver that uses linear programming.
 */
#ifndef MWVCSOLVERLINEARPROGRAMMING_H_
#define MWVCSOLVERLINEARPROGRAMMING_H_

#include "MWVCSolver.h"
#include "LinearProgramSolver.h"
#include "RunningTime.h"

/** An MWVC solver that uses linear programming.
 *
 * Refer to MWVCSolver for the template parameter.
 */
template <class CCG = ConstraintCompositeGraph<> >
class MWVCSolverLinearProgramming : public MWVCSolver<CCG>
{
private:
    std::unique_ptr<LinearProgramSolver> lps;

public:
    /** \brief Construct an MWVCSolverLinearProgramming object with a given linear program
     * solver.
     *
     * \param[in] lps The linear program solver.
     */
    MWVCSolverLinearProgramming(LinearProgramSolver* lps)
    {
        this->lps.reset(lps);
    }

    /** \se{MWVCSolver::solve} */
    virtual double solve(const typename CCG::graph_t& g,
                         typename std::map<typename CCG::variable_id_t, bool>& out,
                         WCSPInstance<> instance)
    {
        using namespace boost;

        if (num_vertices(g) == 0)
            return 0.0;

        typedef typename CCG::graph_t graph_t;
        typedef typename boost::graph_traits<graph_t>::vertex_descriptor vertex_t;
        typedef typename boost::graph_traits<graph_t>::edge_descriptor edge_t;
        typename boost::property_map<graph_t, boost::vertex_name_t>::const_type vertex_id_map;
        typename boost::property_map<graph_t, boost::vertex_weight_t>::const_type vertex_weight_map;


        vertex_id_map = get(vertex_name, g);
        vertex_weight_map = get(vertex_weight, g);

        lps->reset();
        lps->setTimeLimit(RunningTime::GetInstance().getTimeLimit().count());

        // map vertex object to its variable id in the linear program solver
        std::map<vertex_t, LinearProgramSolver::variable_id_t> vertex_to_id;

        // iterate over all vertices and add them as variables.
        typename graph_traits<graph_t>::vertex_iterator vi, vi_end;
        std::tie(vi, vi_end) = vertices(g);
        for (auto it = vi; it != vi_end; ++ it)
            vertex_to_id.insert(std::make_pair(*it, lps->addVariable(vertex_weight_map[*it])));

        lps->setObjectiveType(LinearProgramSolver::ObjectiveType::MIN);

        // iterate over all edges and add them as constraints
        typename graph_traits<graph_t>::edge_iterator ei, ei_end;
        std::tie(ei, ei_end) = edges(g);
        for (auto it = ei; it != ei_end; ++ it)
        {
            std::vector<LinearProgramSolver::variable_id_t> x(2);
            x[0] = vertex_to_id.at(source(*it, g));
            x[1] = vertex_to_id.at(target(*it, g));
            std::vector<double> coeff = {1.0, 1.0};
            lps->addConstraint(x, coeff, 1.0, LinearProgramSolver::ConstraintType::GREATER_EQUAL);
        }

        // solve the LP
        std::vector<double> assignments;
        double opt_value = lps->solve(assignments);

        // assign the results of the LP to the output map
        for (auto it = vi; it != vi_end; ++ it)
        {
            auto id = vertex_id_map[*it];
            if (id >= 0)
                out[id] = assignments.at(vertex_to_id[*it]) > 0.5;
        }

        return opt_value;
    }
};

#endif // MWVCSOLVERLINEARPROGRAMMING_H_
