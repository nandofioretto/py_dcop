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

/** \file WCSPInstance.h
 *
 * Define the definition of WCSP instances and the constraints in it. Algorithms that can be applied
 * directly on WCSP instances, i.e., the min-sum message passing algorithm \cite xkk17 and integer
 * linear programming \cite xkk17a, are also included in this file.
 */

#ifndef WCSPINSTANCE_H_
#define WCSPINSTANCE_H_

#include <array>
#include <cstdint>
#include <istream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

#include <boost/dynamic_bitset.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <cblas.h>

#include "global.h"
#include "RunningTime.h"
#include "LinearProgramSolver.h"

/** \brief Weighted constraint.
 *
 * This class describes a weighted constraint. It consists of the IDs of the variables as well as
 * how the weight corresponding to each assignment.
 *
 * \tparam VarIdType The type of variable IDs. It must be an integer type and defaults to \p
 * intmax_t.
 *
 * \tparam WeightType The type of weights. It must be a numeric type and defaults to \p double.
 *
 * \tparam ValueType The type of values of all variables in the constraint. It should usually be a
 * bitset type and defaults to \p boost::dynamic_bitset<>.
 */
template < class VarIdType = intmax_t,
           class WeightType = double,
           class ValueType = boost::dynamic_bitset<>,  // The type of the values to represent each constraint
           class NonBooleanValueType = size_t>
class Constraint
{
public:
    /** Alias of \p VarIDType. */
    typedef VarIdType variable_id_t;

    /** Alias of \p ValueType. */
    typedef ValueType value_t;

    /** Alias of \p WeightType. */
    typedef WeightType weight_t;

    /** Alias of \p NonBooleanValueType. */
    typedef NonBooleanValueType non_boolean_value_t;

private:
    // This class is only used for Polynomial key comparison. This function ensures keys with
    // a smaller number of variables must precede larger number of variables.
    class PolynomialKeyComparison
    {
    public:
        bool operator () (const std::set<variable_id_t>& a, const std::set<variable_id_t>& b) const
        {
            if (a.size() > b.size())
                return true;

            if (a.size() < b.size())
                return false;

            return a < b;
        }
    };
public:
    /** The polynomial form of constraints consisting of the coefficient of each term (each term is
     * represented by an assignment of values to variables). */
    typedef std::map<std::set<variable_id_t>, weight_t, PolynomialKeyComparison> Polynomial;

private:
    std::vector<variable_id_t> nonBooleanVariables;
    std::vector<variable_id_t> variables;
    std::map<value_t, weight_t> weights;
    std::map<std::vector<non_boolean_value_t>, weight_t> nonBooleanWeights;

public:
    /** Alias of \p Constraint<VarIdType, WeightType, ValueType, NonBooleanValueType>, i.e., the
     * class type itself. */
    typedef Constraint<VarIdType, WeightType, ValueType, NonBooleanValueType> self_t;

    /** \brief Get the list of the IDs of non-Boolean variables in the constraint.
     *
     * \return A list of variable IDs.
     */
    inline const std::vector<variable_id_t>& getNonBooleanVariables() const noexcept
    {
        return nonBooleanVariables;
    }

    /** \brief Get the list of the IDs of variables in the constraint.
     *
     * \return A list of variable IDs.
     */
    inline const std::vector<variable_id_t>& getVariables() const noexcept
    {
        return variables;
    }

    /** \brief Get the ID of the <tt>i</tt>'th variable.
     *
     * \param[in] i The index of the variable of which to get the ID.
     *
     * \return The ID of the <tt>i</tt>'th variable.
     */
    inline variable_id_t getVariable(size_t i) const noexcept
    {
        return variables.at(i);
    }

    /** \brief Set the IDs of the variables in the constraint from a \p std::vector<variable_id_t>
     * object.
     *
     * \param[in] variables: A list of variable IDs to set.
     */
    inline void setVariables(const std::vector<variable_id_t>& variables) noexcept
    {
        this->variables = variables;
        this->weights.clear();
    }

    /** \brief Set the IDs of the non-Boolean variables in the constraint from a \p
     * std::vector<variable_id_t> object.
     *
     * \param[in] variables: A list of variable IDs to set.
     */
    inline void setNonBooleanVariables(const std::vector<variable_id_t>& variables) noexcept
    {
        this->nonBooleanVariables = variables;
        this->weights.clear();
    }

    /** \brief Set the IDs of the variables in the constraint from a range of iterators.
     *
     * \param[in] b the beginning iterator.
     *
     * \param[in] e the ending iterator.
     */
    template<class Iter>
    inline void setVariables(Iter b, Iter e) noexcept
    {
        variables.clear();
        std::copy(b, e, std::back_inserter(variables));
    }

    /** \brief Set the weight of a given assignment of values to variables specified by \p v to \p
     * w.
     *
     * \param[in] v An assignment of values to variables.
     *
     * \param[in] w A weight.
     *
     * \return A reference to the class object itself.
     */
    inline self_t& setWeight(const value_t& v, weight_t w)
    {
        weights[v] = w;
        return *this;
    }

    /** \brief Set the weight of a given assignment of values to non-Boolean variables specified by
     * \p v to \p w.
     *
     * \param[in] v An assignment of values to variables.
     *
     * \param[in] w A weight.
     *
     * \return A reference to the class object itself.
     */
    inline self_t& setWeight(const std::vector<non_boolean_value_t>& v, weight_t w)
    {
        nonBooleanWeights[v] = w;
        return *this;
    }

    /** \brief Get the weight of a given assignment of values to variables specified by \p v.
     *
     * \param[in] v The assignment of values to variables.
     *
     * \return The weight of a given assignment of values to variables specified by \p v.
     */
    inline weight_t getWeight(const value_t& v) const noexcept
    {
        auto it = weights.find(v);
        if (it == weights.end()) // not found, return 0
            return weight_t();

        return it->second;
    }

    /** \brief Get the weight of a given assignment of values to non-Boolean variables specified by
     * \p v.
     *
     * \param[in] v The assignment of values to variables.
     *
     * \return The weight of a given assignment of values to variables specified by \p v.
     */
    inline weight_t getWeight(const std::vector<non_boolean_value_t>& v) const noexcept
    {
        auto it = nonBooleanWeights.find(v);
        if (it == nonBooleanWeights.end()) // not found, return 0
            return weight_t();

        return it->second;
    }

    /** \brief Get a map object that maps assignments of values to variables to weights.
     *
     * \return A map object that maps assignments of values to variables to weights.
     */
    inline const std::map<value_t, weight_t> getWeights() const noexcept
    {
        return weights;
    }

    /** \brief Represent the constraint using a \p boost::property_tree::ptree object.
     *
     * \param[out] t A \p boost::property_tree::ptree object that represents the constraint.
     */
    void toPropertyTree(boost::property_tree::ptree& t) const
    {
        using namespace boost::property_tree;

        t.clear();

        // put the variables
        ptree vs;
        for (auto& v : variables)
            vs.push_back(
                std::make_pair("", ptree(std::to_string(v))));

        t.put_child("variables", vs);

        // put the weights
        ptree ws;
        for (auto& w : weights)
        {
            ptree we;

            for (size_t i = 0; i < getVariables().size(); ++ i)
            {
                if (w.first[i])
                    we.push_back(std::make_pair("", ptree("1")));
                else
                    we.push_back(std::make_pair("", ptree("0")));
            }

            we.push_back(std::make_pair("", ptree(std::to_string(w.second))));

            ws.push_back(std::make_pair("", we));
        }

        t.put_child("weights", ws);
    }

    /** \brief Compute the coefficients of the polynomial converted from a constraint according to
     * \cite k08.
     *
     * \param[out] p A Constraint::Polynomial object corresponding to the polynomial representation
     * of the constraint.
     */
    void toPolynomial(Polynomial& p) const noexcept
    {
        size_t s = getVariables().size();

        // we basically solve A * x = b

        size_t max_int = ((size_t) 1) << s;

        // matrix a
        double * a = new double[max_int * max_int];
        memset(a, 0, max_int * max_int * sizeof(double));

/// \cond
#define ENTRY(a, x, y) a[(y) * max_int + (x)]
/// \endcond
        // set the first column to 1
        for (size_t i = 0; i < max_int; ++ i)
            ENTRY(a, i, 0) = 1.0;
        // Set the lower triangle. The row number corresponds to the assignments of variables, and
        // the col number corresponds to terms of the polynomial in the following order:
        // X_1, X_2, X_1 X_2, X_3, X_1 X_3, X_2 X_3, X_1 X_2 X_3...
        for (size_t i = 1; i < max_int; ++ i)
            for (size_t j = 1; j <= i; ++ j)
                // (i|j)==i : the 1-bits integer i includes all the 1-bits of j
                ENTRY(a, i, j) = ((i | j) == i) ? 1.0 : 0.0;
#undef ENTRY

        // assign the vector b
        double * x = new double[max_int];
        for (size_t i = 0; i < max_int; ++ i)
            x[i] = getWeight(value_t(s, i));

        cblas_dtrsv(CblasColMajor, CblasLower, CblasNoTrans, CblasUnit, max_int, a, max_int, x, 1);
        delete[] a;

        // Insert all the coefficients into the polynomial.
        for (size_t i = 0; i < max_int; ++ i)
        {
            typename Polynomial::key_type k;

            for (size_t j = 0; j < s; ++ j)
                if ((((size_t) 1u) << j) & i)
                    k.insert(getVariable(j));

            p[k] += x[i];
        }

        delete[] x;
    }
};

/** \brief A WCSP instance.
 *
 * This class describes a WCSP instance. It consists a set of constraints.
 *
 * \tparam VarIdType The type of variable IDs. It must be an integer type and defaults to \p
 * intmax_t.
 *
 * \tparam WeightType The type of weights. It must be a numeric type and defaults to \p double.
 *
 * \tparam ConstraintValueType The type of values of all variables in the constraints in the WCSP
 * instance. It should usually be a bitset type and defaults to \p boost::dynamic_bitset<>.
 */
template <class VarIdType = intmax_t, class WeightType = double,
          class ConstraintValueType = boost::dynamic_bitset<>,
          class NonBooleanValueType = size_t>
class WCSPInstance
{
public:
    /** Alias of \p VarIdType. */
    typedef VarIdType variable_id_t;
    /** Alias of \p WeightType. */
    typedef WeightType weight_t;
    /** Alias of \p ConstraintValueType. */
    typedef ConstraintValueType constraint_value_t;
    /** Alias of \p NonBooleanValueType. */
    typedef NonBooleanValueType non_boolean_value_t;

public:
    /** Alias of the Constraint type in the WCSP instance, i.e., \p
     * Constraint<variable_id_t,weight_t,constraint_value_t>.
     */
    typedef Constraint<variable_id_t, weight_t, constraint_value_t> constraint_t;

private:
    std::vector<constraint_t> constraints;

    // map from non-Boolean variables to their Boolean variable representations
    std::vector<std::vector<variable_id_t> > nonBooleanVariables;

public:

    /** \brief Get the mapping from original variables to Boolean variables.
     *
     * \return The mapping.
     */
    inline const std::vector<std::vector<variable_id_t> >& getNonBooleanVariables()
        const noexcept
    {
        return nonBooleanVariables;
    }

    /** \brief Display the mapping from original variables to Boolean variables.
     */
    inline void displayNonBooleanVariableMapping() const noexcept
    {
        std:: cout << "--- Non-Boolean Variable Mapping BEGINS ---" << std::endl;
        for (auto i = 0; i < nonBooleanVariables.size(); ++ i)
        {
            std::cout << i << '\t';
            for (auto j : nonBooleanVariables[i])
            {
                std::cout << j << ' ';
            }
            std::cout << std::endl;
        }
        std:: cout << "--- Non-Boolean Variable Mapping ENDS ---" << std::endl;
    }

    /** \brief Get the list of constraints.
     *
     * \return A list of \p constraint_t objects.
     */
    inline const std::vector<constraint_t>& getConstraints() const noexcept
    {
        return constraints;
    }

    /** \brief Get the <tt>i</tt>'th constraint.
     *
     * \param[in] i The index of the Constraint object to get.
     *
     * \return The <tt>i</tt>'th constraint.
     */
    inline const constraint_t& getConstraint(size_t i) const noexcept
    {
        return constraints.at(i);
    }

    /** \brief Compute the total weight corresponding to an assignment of values to all variables.
     *
     * \param[in] assignments The assignment of values to all variables.
     *
     * \return The computed total weight.
     */
    inline weight_t computeTotalWeight(
        const std::map<variable_id_t, non_boolean_value_t>& assignments) const noexcept
    {
        weight_t tw = 0;

        for (const auto& c : constraints)
        {
            std::vector<non_boolean_value_t> val(c.getNonBooleanVariables().size());
            for (size_t i = 0; i < c.getNonBooleanVariables().size(); ++ i)
            {
                try
                {
                    val[i] = assignments.at(c.getNonBooleanVariables().at(i));
                } catch (std::out_of_range& e)
                {
                    // Here, it means the variable assignments does not hold
                    // c.getNonBooleanVariables().at(i) -- the CCG does not contain that variable.
                    // This may well be that the variable itself is a "dummy" variable -- the value
                    // of it does not affect the total weight. In this case, we always assign zero
                    // (or anything else) to it.
                    val[i] = 0;
                }
            }

            tw += c.getWeight(val);
        }

        return tw;
    }

public:
    /** \brief Load a problem instance from a stream.
     *
     * \param[in] f The input stream.
     */
    void load(std::istream& f);

    /** \brief Load the problem in DIMACS format. The format specification is at
     * http://graphmod.ics.uci.edu/group/WCSP_file_format
     *
     * \param[in] f The input stream.
     */
    void loadDimacs(std::istream& f);

    /** \brief Load the problem in UAI format. The format specification is at
     * http://www.hlt.utdallas.edu/~vgogate/uai14-competition/modelformat.html
     *
     * \param[in] f The input stream.
     */
    void loadUAI(std::istream& f);

    /** List of supported input file formats.
     */
    enum class Format
    {
        DIMACS,
        UAI
    };

    /** \brief Construct a WCSP instance from an input stream in a given format.
     *
     * \param[in] f The input stream.
     *
     * \param[in] format The format of \p f.
     */
    WCSPInstance(std::istream& f, Format format)
    {
        switch (format)
        {
        case Format::DIMACS:
            loadDimacs(f);
            break;
        case Format::UAI:
            loadUAI(f);
            break;
        }
    }

    /** \brief Convert this WCSP instance to a human-readable string.
     *
     * \return The human-readable string.
     */
    std::string toString() const noexcept
    {
        std::stringstream ss;

        ss << '{' << std::endl;
        for (auto& c : constraints)
        {
            ss << c;
        }

        return ss.str();
    }

    /** \brief Solve the WCSP instance using the min-sum message passing algorithm.
     *
     * \param[in] delta The threshold for convergence determination. That is, the algorithm
     * terminates iff all messages change within \p delta compared with the previous iteration.
     *
     * \return A solution to the WCSP instance.
     */
    std::map<variable_id_t, bool> solveUsingMessagePassing(weight_t delta) const noexcept
    {
        std::map<variable_id_t, std::set<const constraint_t*> > constraint_list_for_v;

        // Initialize all messages.
        std::map<std::pair<variable_id_t, const constraint_t*>, std::array<weight_t, 2> > msgs_v_to_c;
        std::map<std::pair<const constraint_t*, variable_id_t>, std::array<weight_t, 2> > msgs_c_to_v;
        for (const auto& c : constraints)
        {
            for (auto v : c.getVariables())
            {
                constraint_list_for_v[v].insert(&c);
                msgs_v_to_c[std::make_pair(v, &c)] = {0, 0};
                msgs_c_to_v[std::make_pair(&c, v)] = {0, 0};
            }
        }

        bool converged = false;
        uintmax_t num_iterations = 0;
        do
        {
            if (RunningTime::GetInstance().isTimeOut())  // time's up
                break;

            ++ num_iterations;

            converged = true;

            auto msgs_v_to_c0 = msgs_v_to_c;
            auto msgs_c_to_v0 = msgs_c_to_v;

            // Update all the messages from variables to constraints.
            for (auto& it : msgs_v_to_c)
            {
                auto v = it.first.first;
                auto c = it.first.second;

                std::array<weight_t, 2> m = {0, 0};

                for (auto nc : constraint_list_for_v.at(v))
                {
                    if (nc != c)
                    {
                        const auto m_to_v = msgs_c_to_v0.find(std::make_pair(nc, v))->second;

                        m[0] += m_to_v.at(0);
                        m[1] += m_to_v.at(1);
                    }
                }

                it.second = m;

                // is it now convergent?
                if (converged)
                {
                    auto old_m = msgs_v_to_c0.at(it.first);

                    if (std::abs(old_m.at(0) - m.at(0)) > delta ||
                        std::abs(old_m.at(1) - m.at(1)) > delta)
                        converged = false;
                }
            }

            // Update all the messages from constraints to variables.
            for (auto& it : msgs_c_to_v)
            {
                auto c = it.first.first;
                auto v = it.first.second;

                std::vector<std::array<weight_t, 2> > m_to_c;
                m_to_c.reserve(c->getVariables().size());
                std::vector<variable_id_t> v_ids;
                v_ids.reserve(c->getVariables().size());
                size_t self_index;   // index of the variable itself
                for (size_t i = 0; i < c->getVariables().size(); ++ i)
                {
                    auto nv = c->getVariable(i);

                    m_to_c.push_back(msgs_v_to_c0.at(std::make_pair(nv, c)));
                    v_ids.push_back(nv);

                    if (nv == v)
                        self_index = i;
                }

                std::array<weight_t, 2> m = {
                    std::numeric_limits<weight_t>::max(), std::numeric_limits<weight_t>::max()
                };

                // TODO: Change the iteration which does not have an upper limit of number of bits.
                for (unsigned long i = 0; i < (1ul << c->getVariables().size()); ++ i)
                {
                    constraint_value_t values(c->getVariables().size(), i);

                    weight_t sum = c->getWeight(values);

                    for (size_t j = 0; j < c->getVariables().size(); ++ j)
                        if (c->getVariable(j) != v)
                            sum += msgs_v_to_c0.at(
                                std::make_pair(c->getVariable(j), c))[values[j] ? 1 : 0];

                    size_t index_update = values[self_index] ? 1 : 0;

                    if (m[index_update] > sum)
                        m[index_update] = sum;
                }

                auto m_min = m[0] < m[1] ? m[0] : m[1];
                m[0] -= m_min;
                m[1] -= m_min;

                it.second = m;

                // is it now convergent?
                if (converged)
                {
                    auto old_m = msgs_c_to_v0.at(it.first);

                    if (std::abs(old_m.at(0) - m.at(0)) > delta ||
                        std::abs(old_m.at(1) - m.at(1)) > delta)
                        converged = false;
                }
            }
        } while (!converged);

        std::cout << "Number of iterations: " << num_iterations << std::endl;

        // compute the variable values
        std::map<variable_id_t, std::array<weight_t, 2> > assignments_w;

        converged = true;
        for (const auto& c : constraints)
            for (auto v : c.getVariables())
            {
                assignments_w[v][0] += msgs_c_to_v[std::make_pair(&c, v)][0];
                assignments_w[v][1] += msgs_c_to_v[std::make_pair(&c, v)][1];
                if (isinf(assignments_w[v][0]) || isinf(assignments_w[v][1]))
                    converged = false;
            }

        std::map<variable_id_t, bool> assignments;
        for (const auto& a : assignments_w)
            assignments[a.first] = a.second[0] > a.second[1] ? a.second[1] : a.second[0];

        if (!converged)
            std::cout << "*** Message passing not converged! ***" << std::endl;

        return assignments;
    }

    /** \brief Solve the WCSP instance using linear programming.
     *
     * \param[in] lps The linear program solver to be used.
     *
     * \return A solution to the WCSP instance.
     */
    std::map<variable_id_t, non_boolean_value_t> solveUsingLinearProgramming(
        LinearProgramSolver& lps) const noexcept
    {
        lps.reset();
        lps.setTimeLimit(RunningTime::GetInstance().getTimeLimit().count());

        lps.setObjectiveType(LinearProgramSolver::ObjectiveType::MIN);

        auto constraints = this->getConstraints();

        // Every variable needs a unary constraint. This is the indices of all unary constraints.
        std::vector<size_t> unary_indices(this->getNonBooleanVariables().size(),
                                                 std::numeric_limits<size_t>::max());
        size_t num_unary = 0;
        for (size_t i = 0; i < constraints.size(); ++ i)
        {
            auto& vs = constraints.at(i).getVariables();
            if (vs.size() == 1)  // unary constraint
            {
                unary_indices[vs.at(0)] = i;
                ++ num_unary;
            }
        }
        constraints.reserve(constraints.size() + unary_indices.size() - num_unary);
        for (variable_id_t i = 0; i < unary_indices.size(); ++ i)
        {
            // no unary constraint for this var
            if (unary_indices.at(i) == std::numeric_limits<size_t>::max())
            {
                constraint_t cons;
                cons.setNonBooleanVariables(std::vector<variable_id_t>{i});
                constraints.push_back(std::move(cons));
                unary_indices[i] = constraints.size() - 1;
            }
        }

        std::vector<std::vector<LinearProgramSolver::variable_id_t> > lp_variables(
            constraints.size());

        // add LP variables and constraints
        for (size_t i = 0; i < constraints.size(); ++ i)
        {
            size_t num_values = 1;
            // Cartesian product of all values
            for (const auto& nbv : constraints.at(i).getNonBooleanVariables())
                num_values *= nonBooleanVariables[nbv].size() + 1;
            lp_variables[i].reserve(num_values);
            for (size_t j = 0; j < num_values; ++ j)  // add all variables
            {
                std::vector<non_boolean_value_t> val;
                val.reserve(constraints.at(i).getNonBooleanVariables().size());

                size_t j0 = j;
                for (const auto& nbv : constraints.at(i).getNonBooleanVariables())
                {
                    size_t d = nonBooleanVariables[nbv].size() + 1;
                    val.push_back(j0 % d);
                    j0 /= d;
                }

                lp_variables[i].push_back(lps.addVariable(constraints.at(i).getWeight(val)));
            }

            // Only one value in a WCSP constraint can take effect.
            lps.addConstraint(lp_variables[i], std::vector<double>(num_values, 1.0), 1.0,
                              LinearProgramSolver::ConstraintType::EQUAL);
        }

        // Add constraints that make sure LP variables that represent overlapped WCSP variables are
        // consistent.
        for (size_t i = 0; i < lp_variables.size(); ++ i)
        {
            for (size_t j : unary_indices)
            {
                if (j <= i)  // Don't do a pair twice.
                    continue;

                // Get the overlap map.
                std::vector<std::pair<size_t, size_t> > overlapped_variables;

                // Whether a variable is overlapping?
                std::vector<bool> vs_overlap_p[2];
                vs_overlap_p[0].resize(constraints.at(i).getNonBooleanVariables().size());
                vs_overlap_p[1].resize(constraints.at(j).getNonBooleanVariables().size());
                std::array<std::vector<size_t>, 2> domain_sizes;
                domain_sizes[0].reserve(constraints.at(i).getNonBooleanVariables().size());
                domain_sizes[1].reserve(constraints.at(j).getNonBooleanVariables().size());
                std::vector<size_t> overlapped_domain_sizes;

                for (size_t z = 0; z < 2; ++ z)
                {
                    size_t c = z ? j : i;
                    for (size_t k = 0; k < constraints.at(c).getNonBooleanVariables().size();
                         ++ k)
                        domain_sizes[z].push_back(
                            nonBooleanVariables[
                                constraints.at(c).getNonBooleanVariables()[k]].size() + 1);
                }

                for (size_t k0 = 0; k0 < constraints.at(i).getNonBooleanVariables().size(); ++ k0)
                    for (size_t k1 = 0; k1 < constraints.at(j).getNonBooleanVariables().size(); ++ k1)
                    {
                        if (constraints.at(i).getNonBooleanVariables()[k0] ==
                            constraints.at(j).getNonBooleanVariables()[k1])
                        {
                            overlapped_variables.push_back(std::make_pair(k0, k1));
                            overlapped_domain_sizes.push_back(
                                nonBooleanVariables[
                                    constraints.at(i).getNonBooleanVariables()[k0]].size() + 1
                                );
                            vs_overlap_p[0][k0] = true;
                            vs_overlap_p[1][k1] = true;
                            break;
                        }
                    }

                std::vector<non_boolean_value_t> vs[2];
                vs[0].resize(constraints.at(i).getNonBooleanVariables().size());
                vs[1].resize(constraints.at(j).getNonBooleanVariables().size());

                if (overlapped_domain_sizes.empty())  // no overlapping
                    continue;
                // Cartesian product of all values of overlapped variables
                size_t num_values = std::accumulate(overlapped_domain_sizes.begin(),
                                                    overlapped_domain_sizes.end(),
                                                    1, std::multiplies<size_t>());

                for (size_t k = 0; k < num_values; ++ k)
                {
                    size_t k0 = k;
                    for (const auto& ov : overlapped_variables)
                    {
                        size_t d = nonBooleanVariables[
                            constraints.at(i).getNonBooleanVariables()[ov.first]].size() + 1;
                        non_boolean_value_t val = k0 % d;
                        k0 /= d;
                        vs[0][ov.first] = val;
                        vs[1][ov.second] = val;
                    }

                    // non-overlapped variables
                    std::array<std::vector<non_boolean_value_t>, 2> vs_non_overlapped;
                    vs_non_overlapped[0].resize((vs[0].size() - overlapped_variables.size()));
                    vs_non_overlapped[1].resize((vs[1].size() - overlapped_variables.size()));

                    std::vector<LinearProgramSolver::variable_id_t> lp_vs;  // LP variables
                    std::vector<double> coefs;

                    for (size_t z = 0; z < 2; ++ z)
                    {
                        size_t l;
                        do {
                            for (l = 0; l < vs[z].size(); ++ l)
                            {
                                if (vs_overlap_p[z][l])
                                    continue;

                                ++ vs[z][l];
                                if (vs[z][l] >= domain_sizes[z][l])
                                    vs[z][l] = 0;
                                else
                                    break;
                            }

                            size_t index = 0;  // index corresponding to the variable values vs[z]
                            size_t cur_base = 1;
                            for (size_t m = 0; m < vs[z].size(); ++ m)
                            {
                                index += cur_base * vs[z][m];
                                cur_base *= domain_sizes[z][m];
                            }

                            if (z == 0)
                            {
                                lp_vs.push_back(lp_variables[i][index]);
                                coefs.push_back(1.0);
                            }
                            else
                            {
                                lp_vs.push_back(lp_variables[j][index]);
                                coefs.push_back(-1.0);
                            }
                        } while (l != vs[z].size());
                    }

                    lps.addConstraint(lp_vs, coefs, 0.0,
                                      LinearProgramSolver::ConstraintType::EQUAL);
                }
            }
        }

        std::vector<double> assignments;
        lps.solve(assignments);

        // Compute the solutions from assignments
        std::map<variable_id_t, non_boolean_value_t> solution;
        for (size_t i : unary_indices)
            for (size_t j = 0; j < lp_variables[i].size(); ++ j)
            {
                if (assignments[lp_variables[i][j]] > 0.99)
                {
                    solution[constraints.at(i).getNonBooleanVariables().at(0)] = j;
                    break;
                }
            }

        return solution;
    }
};

template <class VarIdType, class WeightType, class ConstraintValueType, class NonBooleanValueType>
void WCSPInstance<VarIdType, WeightType, ConstraintValueType, NonBooleanValueType>::loadDimacs(
    std::istream& f)
{
    std::string line;
    std::string tmp;
    size_t max_domain_size;
    size_t nv, nc; // number of variables, number of constraints

    // first line: problem_name number_of_variables max_domain_size number_of_constraints
    // global_upper_bound
    std::getline(f, line);
    std::istringstream ss(line);
    ss >> tmp; // name
    ss >> nv;
    ss >> max_domain_size; // max domain size
    ss >> nc;
    ss >> tmp; // ignore global upper bound

    // domain size of all variables
    std::getline(f, line);
    ss.clear();
    ss.str(line);
    variable_id_t cur_var_id = 0;
    nonBooleanVariables.clear();
    nonBooleanVariables.reserve(nv);
    for (size_t i = 0; i < nv; ++ i)
    {
        size_t domain_size;
        ss >> domain_size;
        // Boolean variables corresponding to the current variable
        std::vector<variable_id_t> vs(domain_size-1);
        std::iota(vs.begin(), vs.end(), cur_var_id);
        cur_var_id += vs.size();
        nonBooleanVariables.push_back(std::move(vs));
    }

    constraints.clear();
    constraints.resize(nc);

    // iterate over constraints
    for (size_t i = 0; i < nc; ++ i)
    {
        size_t arity;
        weight_t default_cost;
        size_t ntuples; // number of tuples not having the default cost
        std::getline(f, line);
        ss.clear();
        ss.str(line);

        ss >> arity;

        // load the variables in the constraint
        std::vector<variable_id_t> non_bool_variables;
        non_bool_variables.reserve(arity);
        // load the corresponding Boolean variables in the constraint
        std::vector<variable_id_t> variables;
        variables.reserve(arity*max_domain_size);
        for (size_t j = 0; j < arity; ++ j)
        {
            variable_id_t vid;
            ss >> vid;
            non_bool_variables.push_back(vid);
            const auto& nbv = nonBooleanVariables[vid];
            variables.insert(variables.end(), nbv.begin(), nbv.end());
        }
        constraints[i].setVariables(std::move(variables));
        constraints[i].setNonBooleanVariables(std::move(non_bool_variables));
        ss >> default_cost;
        // TODO: More efficient handling
        if (default_cost > std::abs(1e-6))   // non-zero default cost
        {
            constraint_value_t values;
            values.resize(constraints[i].getVariables().size());
            unsigned long te = (1u << constraints[i].getVariables().size());
            for (unsigned long l = 0; l < te; ++ l)
            {
                for (unsigned long k = 0; k < values.size(); ++ k)
                    values.set(k, (l & (1u << k)) ? 1 : 0);
                constraints[i].setWeight(values, default_cost);
            }
        }
        ss >> ntuples;

        // load the entries in the constraints
        for (size_t j = 0; j < ntuples; ++ j)
        {
            weight_t cost;
            constraint_value_t values;
            values.resize(constraints[i].getVariables().size());
            values.set();
            std::vector<non_boolean_value_t> non_boolean_values(arity);
            std::getline(f, line);
            ss.clear();
            ss.str(line);
            for (size_t k = 0, cur_bit = 0; k < arity; ++ k)
            {
                int val;
                ss >> val;
                non_boolean_values[k] = val;
                size_t bvs = nonBooleanVariables[constraints[i].getNonBooleanVariables()[k]].size();
                if (bvs == 1)
                    values.set(cur_bit ++, val ? true : false);
                else
                {
                    if (val != 0)
                        values.set(cur_bit + val - 1, false);
                    cur_bit += bvs;
                }
            }
            ss >> cost;
            constraints[i].setWeight(std::move(non_boolean_values), cost);
            constraints[i].setWeight(std::move(values), cost);
        }
    }
}

template <class VarIdType, class WeightType, class ConstraintValueType, class NonBooleanValueType>
void WCSPInstance<VarIdType, WeightType, ConstraintValueType, NonBooleanValueType>::loadUAI(
    std::istream& f)
{
    std::string line;
    std::string tmp;
    size_t nv, nc; // number of variables, number of constraints

    // first line: MARKOV, just ignore it
    std::getline(f, tmp);

    // second line: number of variables
    {
        std::getline(f, line);
        std::istringstream ss(line);
        ss >> nv; // number of variables
    }

    // third line: arity
    {
        std::getline(f, line);
        std::istringstream ss(line);
        variable_id_t cur_var_id = 0;
        nonBooleanVariables.clear();
        nonBooleanVariables.reserve(nv);
        for (size_t i = 0; i < nv; ++ i)
        {
            size_t domain_size;
            ss >> domain_size;
            // Boolean varaibles corresponding to the current variable
            std::vector<variable_id_t> vs(domain_size-1);
            std::iota(vs.begin(), vs.end(), cur_var_id);
            cur_var_id += vs.size();
            nonBooleanVariables.push_back(std::move(vs));
        }
    }

    // fourth line: number of constraints
    {
        std::getline(f, line);
        std::istringstream ss(line);
        ss >> nc;
        constraints.clear();
        constraints.resize(nc);
    }

    // iterate over constraints
    for (size_t i = 0; i < nc; ++ i)
    {
        size_t arity;
        std::getline(f, line);
        std::istringstream ss(line);

        ss >> arity;

        // Load the variables in the constraint. We load it reversely because UAI format arrange
        // their constraint value reversely as we do.
        std::vector<variable_id_t> variables;
        std::vector<variable_id_t> non_bool_variables(arity);

        for (size_t j = 0; j < arity; ++ j)
        {
            variable_id_t vid;
            ss >> vid;
            non_bool_variables[arity-j-1] = vid;
            variables.insert(variables.end(),
                             nonBooleanVariables[vid].rbegin(),
                             nonBooleanVariables[vid].rend());
        }
        std::reverse(variables.begin(), variables.end());

        constraints[i].setVariables(std::move(variables));
        constraints[i].setNonBooleanVariables(std::move(non_bool_variables));
    }

    // iterate over constraints
    for (size_t i = 0; i < nc; ++ i)
    {
        size_t ntuples;
        f >> ntuples;  // number of entries

        // load the entries in the constraints
        std::vector<weight_t> costs(ntuples);
        for (size_t j = 0; j < ntuples; ++ j)
            f >> costs[j];

        // normalization constant
        weight_t sum(std::accumulate(costs.begin(), costs.end(), weight_t()));

        // set the value of each tuple
        for (size_t j = 0; j < ntuples; ++ j)
        {
            costs[j] = -std::log(costs[j] / sum);
            if (!std::isfinite(costs[j]))
                costs[j] = 1e6;
            constraint_value_t values;
            std::vector<non_boolean_value_t> non_boolean_values;
            non_boolean_values.reserve(constraints[i].getNonBooleanVariables().size());
            size_t j0 = j;
            for (const auto& nbv : constraints[i].getNonBooleanVariables())
            {
                auto d = nonBooleanVariables[nbv].size() + 1;
                size_t cur_val = j0 % d;
                non_boolean_values.push_back(cur_val);

                if (d == 2)
                    values.push_back(cur_val ? true : false);
                else
                {
                    for (size_t k = 1; k < d; ++ k)
                    {
                        if (cur_val == k)
                            values.push_back(false);
                        else
                            values.push_back(true);
                    }
                }
                j0 /= d;
            }
            constraints[i].setWeight(std::move(values), costs[j]);
            constraints[i].setWeight(std::move(non_boolean_values), costs[j]);
        }
    }
}

/** \brief Write a Constraint object to a stream in a human-readable form.
 *
 * \param[in] o The stream to write to.
 *
 * \param[in] c The constraint object to be write to \p o.
 *
 * \return The stream \p o.
 */
template <class ...T>
std::ostream& operator << (std::ostream& o, const Constraint<T...>& c)
{
    boost::property_tree::ptree t;
    c.toPropertyTree(t);
    boost::property_tree::write_json(o, t, true);
    return o;
}

#endif /* WCSPINSTANCE_H_ */
