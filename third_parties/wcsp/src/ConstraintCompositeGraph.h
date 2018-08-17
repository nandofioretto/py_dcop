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

/** \file ConstraintCompositeGraph.h
 *
 * Define classes and functions related to the Constraint Composite Graph (CCG).
 */

#ifndef CONSTRAINTCOMPOSITEGRAPH_H_
#define CONSTRAINTCOMPOSITEGRAPH_H_

#include <array>
#include <map>
#include <ostream>
#include <vector>

#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graphviz.hpp>

#include "WCSPInstance.h"

/// \cond
namespace boost
{
    enum vertex_weight_t { vertex_weight };
    BOOST_INSTALL_PROPERTY(vertex, weight);
}
/// \endcond

/** \brief A CCG.
 *
 * This class describes a CCG.
 *
 * \tparam Constraint The constraint type. It defaults to \p WCSPInstance<>::constraint_t.
 */
template <class Constraint = WCSPInstance<>::constraint_t>
class ConstraintCompositeGraph
{
public:
    /** Alias of \p ConstraintCompositeGraph<Constraint>. */
    typedef ConstraintCompositeGraph<Constraint> self_t;
    /** Alias of \p Constraint::variable_id_t. */
    typedef typename Constraint::variable_id_t variable_id_t;
    /** Alias of \p Constraint::weight_t. */
    typedef typename Constraint::weight_t weight_t;

private:
    // define graph properties
    typedef boost::property<boost::vertex_name_t, variable_id_t, /* vertex ID */
            boost::property<boost::vertex_weight_t, weight_t> > VertexProperties;

public:
    /** The data type of the graph that represents a CCG. */
    typedef boost::adjacency_list<boost::vecS, boost::listS, boost::undirectedS,
            VertexProperties, boost::no_property> graph_t;

private:
    typedef typename boost::graph_traits<graph_t>::vertex_descriptor vertex_t;
    typedef typename boost::graph_traits<graph_t>::edge_descriptor edge_t;

private:
    graph_t g;
    std::map<variable_id_t, vertex_t> id_to_v; // map from variable id to vertex_t

    typename boost::property_map<graph_t, boost::vertex_name_t>::type vertex_id_map;
    typename boost::property_map<graph_t, boost::vertex_weight_t>::type vertex_weight_map;

public:
    /** \brief Get a pointer to a \p graph_t object that represents the CCG.
     *
     * \return A pointer to a \p graph_t object that represents the CCG.
     */
    const graph_t* getGraph() const noexcept
    {
        return &g;
    }

    /** \brief Get the number of variables of the WCSP instance with which the CCG is associated.
     *
     * \return The number of variables of the WCSP instance with which the CCG is associated.
     */
    size_t getNumberOfVariables() const noexcept
    {
        return id_to_v.size();
    }

    /** \brief Get the number of variable vertices, type 1 auxiliary vertices, and type 2 auxiliary
     * vertices.
     *
     * Variable vertices are the vertices that represent variables. Type 1 auxiliary vertices are
     * the &ldquo;flower root&rdquo; vertices (green vertices in Figure 8 in \cite k08). Type
     * 2auxiliary vertices are the &ldquo;thorn&rdquo; vertices (red vertices in Figure 8 in \cite
     * k08).
     *
     * \return An array of three integers representing the number of variable vertices, type 1
     * auxiliary vertices, and type 2 auxiliary vertices.
     */
    inline std::array<size_t, 3> getStatistics() const noexcept
    {
        using namespace boost;

        typename graph_traits<graph_t>::vertex_iterator vi, vi_end, next;

        std::array<size_t, 3> ret = {};

        std::tie(vi, vi_end) = vertices(g);

        for (auto it = vi; it != vi_end; ++ it)
        {
            switch (vertex_id_map[*it])
            {
            case -1:
                ++ ret[1];
                break;
            case -2:
                ++ ret[2];
                break;
            default:
                ++ ret[0];
                break;
            }
        }

        return ret;
    }

private:
    /*
     * Add a vertex corresponding to v or get the vertex if exists.
     */
    vertex_t addOrGetVertex(variable_id_t v) noexcept
    {
        using namespace boost;

        auto v_pos = id_to_v.find(v); // the iterator of the vertex in the id_to_v map

        if (v_pos == id_to_v.end()) // the variable has never been added to the CCG
        {
            auto ver = add_vertex(g);
            vertex_id_map[ver] = v;
            v_pos = id_to_v.insert(std::make_pair(v, ver)).first;
        }
        return v_pos->second;
    }

public:
    /** \brief The default constructor. */
    ConstraintCompositeGraph()
    {
        using namespace boost;

        vertex_id_map = get(vertex_name, g);
        vertex_weight_map = get(vertex_weight, g);
    }

    /** \brief Add a polynomial into the CCG.
     *
     * \param[in] p The polynomial to add. We note that \p p will be modified in this function:
     * According to the procedure described in \cite k08, when converting high-order terms to CCG
     * gadget, lower-order terms are updated.
     *
     * \return The constant term of the modified polynomial.
     */
    weight_t addPolynomial(typename Constraint::Polynomial& p) noexcept
    {
        using namespace boost;
        typedef typename Constraint::Polynomial::key_type PolynomialKey;

        // the iteration is guaranteed to be from the coefficients corresponding to the largest
        // number of variables to the smallest.
        for (const auto& item : p)
        {
            const PolynomialKey& k = item.first;
            weight_t w = item.second;

            if (std::abs(w) < 1e-6) // ignore very small weights
                continue;

            if (k.empty())  // constant term
                continue;

            if (k.size() == 1) // linear term
            {
                variable_id_t v = *k.begin();

                // add the weight
                auto vertex = addOrGetVertex(v);
                if (w >= 0)
                    vertex_weight_map[vertex] += w;
                else
                {
                    // add the auxiliary vertex with a weight of -w and connect them
                    auto vertex_a = add_vertex(g);
                    vertex_id_map[vertex_a] = -1; // no corresponding variable
                    vertex_weight_map[vertex_a] = -w;
                    add_edge(vertex, vertex_a, g);
                }

                continue;
            }

            // non-linear term

            std::vector<vertex_t> vers;
            vers.reserve(k.size());
            for (auto va : k)
                vers.push_back(addOrGetVertex(va));


            if (w < 0) // negative weight
            {
                w = -w;
                p[PolynomialKey()] -= w;
                // auxiliary vertex
                auto vertex_a = add_vertex(g);
                vertex_weight_map[vertex_a] = w;
                vertex_id_map[vertex_a] = -1;

                for (auto v : vers)
                    add_edge(v, vertex_a, g);
            }
            else // non negative weight
            {
                // Always attach L to the first variable. Update lower order coefficients.
                double l = w + 1;
                p[PolynomialKey()] -= l + w;
                p[PolynomialKey{*k.begin()}] += l;
                p[PolynomialKey(std::next(k.begin()), k.end())] += w;

                auto vertex_a = add_vertex(g);
                vertex_weight_map[vertex_a] = w;
                vertex_id_map[vertex_a] = -1;
                auto vertex_a1 = add_vertex(g);
                vertex_weight_map[vertex_a1] = l;
                vertex_id_map[vertex_a1] = -2;

                add_edge(vertex_a, vertex_a1, g);
                add_edge(vertex_a1, vers.at(0), g);

                // connect the auxiliary vertex to all other variable vertices
                for (auto it = std::next(vers.begin()); it != vers.end(); ++ it)
                    add_edge(vertex_a, *it, g);
            }
        }

        // return the constant term
        return p[PolynomialKey()];
    }

    /** \brief Build the cliques that represent every single variable.
     *
     * \param[in] variables The mapping from non-Boolean variables to Boolean variables.
     */
    inline void addCliques(const std::vector<std::vector<variable_id_t> >& variables)
        noexcept
    {
        using namespace boost;

        for (const auto& nbv : variables)
        {
            if (nbv.size() == 1)
                continue;

            // all vertices that represent the variable
            std::vector<vertex_t> all_vertices;
            all_vertices.reserve(nbv.size());
            for (const auto& id : nbv)
            {
                // id_to_v does not contain id, which means that nbv may not appear in the WCSP at
                // all.
                if (id_to_v.count(id) == 0)
                    return;

                all_vertices.push_back(id_to_v.at(id));
            }

            // Connect every two vertices in all_vertices
            for (auto it = all_vertices.begin(); it != all_vertices.end(); ++ it)
                for (auto it1 = std::next(it); it1 != all_vertices.end(); ++ it1)
                    add_edge(*it, *it1, g);
        }
    }

    /** \brief Simplify the graph by removing all zero weight vertices and all edges incident to
     * them.
     *
     * \param[in,out] out If any variable vertex is simplified out, \p out should have the value of
     * the corresponding variable key set to \p true.
     */
    inline void simplify(std::map<variable_id_t, bool>& out) noexcept
    {
        using namespace boost;

        typename graph_traits<graph_t>::vertex_iterator vi, vi_end, next;

        // remove all vertices with a weight of 0
        std::tie(vi, vi_end) = vertices(g);
        for (next = vi; vi != vi_end; vi = next)
        {
            ++ next;
            if (std::abs(vertex_weight_map[*vi]) < 1e-6)
            {
                auto id = vertex_id_map[*vi];
                if (id >= 0)
                    out[id] = true;
                clear_vertex(*vi, g);
                remove_vertex(*vi, g);
            }
        }
    }

    /** \brief Write the CCG's graphviz representation to a stream.
     *
     * \param[out] o The stream to write to.
     */
    inline void toGraphviz(std::ostream& o) const noexcept
    {
        using namespace boost;

        std::map<vertex_t, int> map_v_to_id;

        auto vs = vertices(g);
        int i = 0;
        for (auto v = vs.first; v != vs.second; ++ v)
            map_v_to_id[v] = i ++;

        write_graphviz(o, g,
                       [this](std::ostream& o, const vertex_t& v) {
                           o << "[label=\"id=" << vertex_id_map[v] << ",weight=" << vertex_weight_map[v] << "\"]";
                       },
                       default_writer(), default_writer(),
                       make_assoc_property_map(map_v_to_id));
    }

    /** \brief Write the CCG's DIMACS format representation to a stream.
     *
     * @param[out] o The stream to write to.
     * @param[in] no_negative Whether variable IDs should all be positive.
     */
    inline void toDimacs(std::ostream& o, bool no_negative = false) const noexcept
    {
        using namespace boost;

        auto g = this->g;

        o << "p edges " << num_vertices(g) << ' ' << num_edges(g) << std::endl;

        auto all_v = vertices(g);

        // vertices
        variable_id_t next_id = 0;
        std::map<vertex_t, variable_id_t> id_map;  // only used for no_negative = true
        for (auto it = all_v.first; it != all_v.second; ++ it)
        {
            variable_id_t id;
            if (no_negative)
            {
                id = next_id ++;
                // The variable IDs of a weighted graph start from 1.
                id_map[*it] = id + 1;
            }
            else
                id = vertex_id_map[*it];

            o << "v " << id + 1 << ' ' << vertex_weight_map[*it] << std::endl;
        }

        // edges
        auto all_e = edges(g);
        for (auto it = all_e.first; it != all_e.second; ++ it)
            if (no_negative)
                o << "e " << id_map[source(*it, g)] << ' ' << id_map[target(*it, g)] << std::endl;
            else
                o << "e " <<
                    vertex_id_map[source(*it, g)] << ' ' <<
                    vertex_id_map[target(*it, g)] << std::endl;


        if (no_negative)
        {
            std::cout << "--- vertex types begin ---" << std::endl;

            for (auto it = all_v.first; it != all_v.second; ++ it)
                std::cout << id_map[*it] << ' ' << vertex_id_map[*it] << std::endl;

            std::cout << "--- vertex types end ---" << std::endl;
        }
    }
};


/** \brief Write a CCG to a stream in a human-readable form.
 *
 * \param[out] o The stream to write to.
 * \param[in] ccg The CCG to write to \p o.
 *
 * \return The stream \p o.
 */
template <class ...T>
std::ostream& operator << (std::ostream& o, const ConstraintCompositeGraph<T...>& ccg)
{
    ccg.toGraphviz(o);

    return o;
}

#endif /* CONSTRAINTCOMPOSITEGRAPH_H_ */
