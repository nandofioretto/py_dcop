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

/** \file LinearProgramSolver.h
 */

#ifndef LINEARPROGRAMSOLVER_H_
#define LINEARPROGRAMSOLVER_H_

#include <exception>
#include <sstream>
#include <string>
#include <vector>

/** The base class of all linear program solvers.
 */
class LinearProgramSolver
{
public:
    /** Type of variable IDs in the linear program. */
    typedef int variable_id_t;
    /** Type of constraint IDs in the linear program. */
    typedef int constraint_id_t;

    /** Type of LP variables, e.g., continuous, binary, etc. */
    enum class VarType
    {
        CONTINUOUS,
        BINARY
    };

    /** Type of LP constraints, e.g., less equal, greater equal, etc. */
    enum class ConstraintType
    {
        LESS_EQUAL,
        GREATER_EQUAL,
        EQUAL
    };

    /** Type of objectives, either minimization or maximization. */
    enum class ObjectiveType
    {
        MIN,
        MAX
    };

    /** \brief Solve the linear program.
     *
     * \param[out] assignment The solution to the linear program.
     *
     * \return The objective function value of the optimal solution.
     */
    virtual double solve(std::vector<double>& assignment) = 0;

    /** The default destructor. */
    virtual ~LinearProgramSolver();

    /** \brief Add a variable, return its ID, or -1 if error.
     *
     * \param[in] coefficient The coefficient of the variable in the objective function.
     *
     * \param[in] type The type of the variable.
     *
     * \param[in] lb The lower bound of the variable.
     *
     * \param[in] ub The upper bound of the variable.
     *
     * \return The ID of the variable.
     */
    virtual variable_id_t addVariable(double coefficient, VarType type = VarType::BINARY,
                                      double lb = 0.0, double ub = 1.0) = 0;

    /** \brief Add a constraint.
     *
     * \param[in] variables Variables involved in this constraint.
     *
     * \param[in] coefficients Coefficients of the variables in this constraint.
     *
     * \param[in] rhs The right-hand side of the constraint (inequation).
     *
     * \param[in] type Type of the constraint.
     *
     * \return The ID of the constraint, or -1 if an error occurred.
     */
    virtual constraint_id_t addConstraint(const std::vector<variable_id_t>& variables,
                                          const std::vector<double>& coefficients, double rhs = 0.0,
                                          ConstraintType type = ConstraintType::LESS_EQUAL) = 0;

    /** \brief Set the objective type.
     *
     * \param type The type of the objective to set.
     *
     * \remark This function must be called before solving since there is no default objective type.
     */
    virtual void setObjectiveType(ObjectiveType type) = 0;

    /** \brief Reset the solver, e.g., clearing all variables and constraints. */
    virtual void reset() = 0;

    /** \brief Set the time limit for running the solver.
     *
     * \param[in] t The time limit in seconds.
     */
    virtual void setTimeLimit(double t) = 0;

    /** The base class of all linear program solver exceptions.
     */
    class Exception : public std::exception
    {
    private:
        std::string msg;
    public:
        /** \brief Construct an Exception with an error message.
         *
         * \param[in] msg The error message.
         */
        inline Exception(const std::string& msg) noexcept
        {
            this->msg = "LinearProgramSolver exception: " + msg;
        }

        /** \brief Give an explanation of the exception.
         *
         * \return The explanatory string.
         */
        inline const char* what() const noexcept
        {
            return msg.data();
        }
    };

    /** Timeout exception.
    */
    class TimeOutException : public Exception
    {
    public:
        /** \brief Construct a TimeOutException object with an error message.
         *
         * \param[in] msg The error message.
         */
        inline TimeOutException(const std::string& msg) noexcept
            : Exception("Time out" + (msg.empty() ? "" : (": " + msg)))
        {}
    };
};


#endif /* LINEARPROGRAMSOLVER_H_ */
