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

/** \file MWVCSolverMessagePassing.h
 *
 * Define the MWVC solver that uses the min-sum message passing algorithm as shown in \cite xkk17.
 */

#ifndef MWVCSOLVERMESSAGEPASSING_H_
#define MWVCSOLVERMESSAGEPASSING_H_

#include <array>
#include <cmath>
#include <map>
#include <utility>
#include <tuple>
#include <chrono>

#include <boost/any.hpp>

#include "ConstraintCompositeGraph.h"
#include "MWVCSolver.h"
#include "WCSPInstance.h"

using namespace std;

/** The MWVC solver that uses the min-sum message passing algorithm as shown in \cite xkk17.
 *
 * Refer to MWVCSolver for the template parameter.
 */
template <class CCG = ConstraintCompositeGraph<> >
class MWVCSolverMessagePassing : public MWVCSolver<CCG>
{
private:
    typedef typename CCG::graph_t graph_t;
    typedef typename CCG::weight_t weight_t;
    typedef typename boost::graph_traits<graph_t>::vertex_descriptor vertex_t;
    typedef typename boost::graph_traits<graph_t>::edge_descriptor edge_t;
    typedef std::map<typename boost::graph_traits<graph_t>::edge_descriptor, weight_t> lambda_t;

    double delta;  // tolerance

public:

    /** \brief Construct an MWVCSolverMessagePassing object with a given convergence threshold.
     *
     * \param[in] delta The threshold for convergence determination.
     */
    MWVCSolverMessagePassing(double delta)
        : delta(delta)
    {}

    /** \se{MWVCSolver::solve} */
    virtual double solve(const graph_t& g,
                         typename std::map<typename CCG::variable_id_t, bool>& out,
                          WCSPInstance<> instance)

    {
        using namespace boost;
	std::cout << "ccg-maxsum-results-start\n";
	
        /* initialize random seed: */
        srand (time(NULL));

        if (num_vertices(g) == 0)
            return 0.0;

        const auto vertex_id_map = get(vertex_name, g);
        const auto vertex_weight_map = get(vertex_weight, g);

        typename graph_traits<graph_t>::edge_iterator ei, ei_end;
        std::tie(ei, ei_end) = edges(g);

        typename graph_traits<graph_t>::vertex_iterator vi, vi_end;
        std::tie(vi, vi_end) = vertices(g);

        // Initialize all messages. The first element is for x = 0 and the second is for x = 1.
        std::map<std::pair<vertex_t, vertex_t>, std::array<weight_t, 2> > msgs;
        for (auto it = ei; it != ei_end; ++ it)
        {
            std::array<vertex_t, 2> vs = {source(*it, g), target(*it, g)};
            // All messages are initialized to 0.
            msgs[std::make_pair(vs[0], vs[1])] = {0, 0};
            msgs[std::make_pair(vs[1], vs[0])] = {0, 0};
        }

        bool converged = false;
        double total_weight = 0.0;
        uintmax_t num_iterations = 0;
        uintmax_t net_load = 0;
        uintmax_t best_cost = 1e10;


        typedef std::chrono::high_resolution_clock Time;
        typedef std::chrono::duration<float> fsec;

        auto start = Time::now();
 

        do
        {
            if (RunningTime::GetInstance().isTimeOut())  // time's up
                break;

            ++ num_iterations;

            converged = true;

            auto msgs0 = msgs;

            // Update all the messages.
            for (auto& it : msgs)
            {
                auto v_from = it.first.first;
                auto v_to = it.first.second;

                std::array<weight_t, 2> m = {vertex_weight_map[v_from], 0};
                weight_t m2[2] = {0, vertex_weight_map[v_from]};
                for (auto neighbors = adjacent_vertices(v_from, g);
                     neighbors.first != neighbors.second; ++ neighbors.first)
                {
                    if (*neighbors.first == v_to)
                        continue;

                    // For x = 0, we know the other vertex must be covered.
                    m[0] += msgs0[std::make_pair(*neighbors.first, v_from)].at(1);
                    m2[0] += msgs0[std::make_pair(*neighbors.first, v_from)].at(0);
                    m2[1] += msgs0[std::make_pair(*neighbors.first, v_from)].at(1);
                }

                m[1] = m2[0] < m2[1] ? m2[0] : m2[1];

                auto old_m = msgs0[std::make_pair(v_from, v_to)];


                double alpha = num_iterations < 200 ? 0.9 : 0.7;
                m[0] = old_m[0] * alpha + m[0] * (1-alpha);
                m[1] = old_m[1] * alpha + m[1] * (1-alpha);

                // Add random noise to message
                //if (num_iterations > 100) {
                   m[0] += rand() % 2 + 1;
                   m[1] += rand() % 2 + 1;
                //}

                auto m_min = m[0] < m[1] ? m[0] : m[1];
                m[0] -= m_min;
                m[1] -= m_min;

                it.second = m;

                net_load++;


                // is it now convergent?
                if (converged)
                {
                    auto old_m = msgs0.at(it.first);

                    if (std::abs(old_m.at(0) - m.at(0)) > delta ||
                        std::abs(old_m.at(1) - m.at(1)) > delta)
                        converged = false;
                }
            }

            fsec curr_time = Time::now() - start;



            // compute the MWVC
            double total_weight = 0.0;
            converged = true;
            for (auto it = vi; it != vi_end; ++ it)
            {
                weight_t min0 = 0, min1 = 0;
                for (auto neighbors = adjacent_vertices(*it, g);
                     neighbors.first != neighbors.second; ++ neighbors.first)
                {
                    auto m = msgs.at(std::make_pair(*neighbors.first, *it));
                    min0 += m.at(0);
                    min1 += m.at(1);
                }

                min1 += vertex_weight_map[*it];

                auto id = vertex_id_map[*it];
                if (std::isinf(min0) || std::isinf(min1))
                    converged = false;
                if (min0 > min1)
                {
                    if (id >= 0)
                        out[id] = true;
                    total_weight += vertex_weight_map[*it];
                }
                else
                    if (id >= 0)
                        out[id] = false;
            }

            std::map<WCSPInstance<>::variable_id_t, WCSPInstance<>::non_boolean_value_t> solution;
            for (WCSPInstance<>::variable_id_t v = 0; v < instance.getNonBooleanVariables().size(); ++ v)
            {
                const auto& bvs = instance.getNonBooleanVariables()[v];

                // no assignment specified for bvs[0], which mean it can be any value (e.g., not in the
                // WCSP). No need to modify solution.
                if (out.count(bvs[0]) == 0)
                    continue;

                if (bvs.size() == 1)
                {
                    solution[v] = out.at(bvs[0]);
                    continue;
                }

                auto false_v = std::find_if_not(
                    bvs.begin(), bvs.end(),
                    [&](ConstraintCompositeGraph<>::variable_id_t id){return out.at(id);});

                if (false_v == bvs.end())  // No variable is false
                    solution[v] = 0;
                else
                    solution[v] = std::distance(bvs.begin(), false_v) + 1;
            }

            uintmax_t a = instance.computeTotalWeight(solution);
            
            if (best_cost > a) best_cost = a;
            std::cout << num_iterations << "\t" << best_cost << "\t" << net_load << "\t" 
                      << curr_time.count() << endl;

            //std::cout << num_iterations << "\t" << instance.computeTotalWeight(out) << "\t" << net_load << std::endl;


        } while (num_iterations < 5000);
	std::cout << "ccg-maxsum-results-end\n";

        // std::cout << "Number of iterations: " << num_iterations << std::endl;

        if (!converged)
            std::cout << "*** Message passing not converged! ***" << std::endl;

        return total_weight;
    }
};

#endif // MWVCSOLVERMESSAGEPASSING_H_
