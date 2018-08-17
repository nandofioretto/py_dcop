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

/** \file LinearProgramSolverGurobi.h
 *
 * Define the class that solves a linear program using the Gurobi Optimizer.
 */

#ifdef HAVE_GUROBI

#ifndef LINEARPROGRAMSOLVERGUROBI_H_
#define LINEARPROGRAMSOLVERGUROBI_H_

#include <memory>
#include <vector>

#include <gurobi_c++.h>

#include "LinearProgramSolver.h"

/** The linear program solver using the Gurobi Optimizer.
 */
class LinearProgramSolverGurobi: public LinearProgramSolver
{
private:
    std::unique_ptr<GRBEnv> gurobiEnv;
    std::unique_ptr<GRBModel> gurobiModel;

    // all the objective coefficients
    std::vector<double> objectiveCoefficients;

    // all the gurobi variable objects
    std::vector<GRBVar> gurobiVariables;

    // all the gurobi constraint objects
    std::vector<GRBConstr> gurobiConstraints;
public:
    /** \brief The default constructor. */
    LinearProgramSolverGurobi();
    /** \brief The default destructor. */
    virtual ~LinearProgramSolverGurobi();
    /** \se{LinearProgramSolver::addVariable} */
    virtual variable_id_t addVariable(double coefficient, VarType type = VarType::BINARY,
                                      double lb = 0.0, double ub = 1.0);
    /** \se{LinearProgramSolver::addConstraint} */
    virtual constraint_id_t addConstraint(const std::vector<variable_id_t>& variables,
                                      const std::vector<double>& coefficients, double rhs = 0.0,
                                      ConstraintType type = ConstraintType::LESS_EQUAL);
    /** \se{LinearProgramSolver::setObjectiveType} */
    virtual void setObjectiveType(ObjectiveType type);
    /** \se{LinearProgramSolver::solve} */
    virtual double solve(std::vector<double>& assignments);
    /** \se{LinearProgramSolver::reset} */
    virtual void reset();
    /** \se{LinearProgramSolver::setTimeLimit} */
    virtual void setTimeLimit(double t);
};

#endif /* LINEARPROGRAMSOLVERGUROBI_H_ */

#endif // HAVE_GUROBI
