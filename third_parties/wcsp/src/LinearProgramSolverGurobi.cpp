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

#ifdef HAVE_GUROBI

#include "LinearProgramSolverGurobi.h"
#include <iostream>

LinearProgramSolverGurobi::LinearProgramSolverGurobi()
{
    try
    {
        gurobiEnv.reset(new GRBEnv());
        gurobiEnv->set(GRB_IntParam_Threads, 1);  // single thread
        gurobiModel.reset(new GRBModel(*gurobiEnv));
    } catch (GRBException e)
    {
        std::cerr << "Gurobi Error code: " << e.getErrorCode() << std::endl;
        throw e;
    }
}

LinearProgramSolverGurobi::~LinearProgramSolverGurobi() = default;

LinearProgramSolver::variable_id_t LinearProgramSolverGurobi::addVariable(
    double coefficient, VarType type, double lb, double ub)
{
    char gurobi_type;

    switch (type)
    {
    case VarType::BINARY:
        gurobi_type = GRB_BINARY;
        break;
    case VarType::CONTINUOUS:
        gurobi_type = GRB_CONTINUOUS;
        break;
    }

    // Store the variable object in an array
    gurobiVariables.push_back(
        gurobiModel->addVar(lb, ub, coefficient, gurobi_type));

    objectiveCoefficients.push_back(coefficient);

    return gurobiVariables.size() - 1;
}

LinearProgramSolver::constraint_id_t LinearProgramSolverGurobi::addConstraint(
    const std::vector<variable_id_t>& variables,
    const std::vector<double>& coefficients, double rhs,
    ConstraintType type)
{
    if (variables.empty())
        return -1;

    // Get the corresponding Gurobi constraint type from our definition of constraint type.
    char gurobi_type;

    switch (type)
    {
    case ConstraintType::LESS_EQUAL:
        gurobi_type = GRB_LESS_EQUAL;
        break;
    case ConstraintType::GREATER_EQUAL:
        gurobi_type = GRB_GREATER_EQUAL;
        break;
    case ConstraintType::EQUAL:
        gurobi_type = GRB_EQUAL;
        break;
    }

    // Construct the left hand side expression.
    GRBLinExpr lhs_expr;
    for (size_t i = 0; i < variables.size(); ++ i)
        lhs_expr.addTerms(&coefficients[i], &gurobiVariables.at(variables[i]), 1);

    gurobiConstraints.push_back(gurobiModel->addConstr(lhs_expr, gurobi_type, rhs));

    return gurobiConstraints.size() - 1;
}

void LinearProgramSolverGurobi::setObjectiveType(ObjectiveType type)
{
    char gurobi_type;

    switch (type)
    {
    case ObjectiveType::MIN:
        gurobi_type = GRB_MINIMIZE;
        break;
    case ObjectiveType::MAX:
        gurobi_type = GRB_MAXIMIZE;
        break;
    }

    gurobiModel->update();

    // Construct the objective expression.
    GRBLinExpr expr;
    expr.addTerms(&objectiveCoefficients[0],
                  &gurobiVariables[0], gurobiVariables.size());

    gurobiModel->setObjective(expr, gurobi_type);
}

double LinearProgramSolverGurobi::solve(std::vector<double>& assignments)
{
    assignments.clear();

    gurobiModel->update();

    try
    {
        gurobiModel->optimize();
        if (gurobiModel->get(GRB_IntAttr_Status) == GRB_TIME_LIMIT)
            throw LinearProgramSolver::TimeOutException("");

        // Assign the values of the variables.
        assignments.reserve(gurobiVariables.size());
        for (auto& v : gurobiVariables)
            assignments.push_back(v.get(GRB_DoubleAttr_X));
    } catch (GRBException e)
    {
        return 0.0;
    }

    return gurobiModel->get(GRB_DoubleAttr_ObjVal);
}

void LinearProgramSolverGurobi::reset()
{
    objectiveCoefficients.clear();
    gurobiVariables.clear();
    gurobiConstraints.clear();
    std::unique_ptr<GRBEnv> env = std::move(gurobiEnv);
    gurobiEnv.reset(new GRBEnv());
    gurobiEnv->set(GRB_IntParam_Threads, 1);  // single thread
    gurobiModel.reset(new GRBModel(*gurobiEnv));
}

void LinearProgramSolverGurobi::setTimeLimit(double t)
{
    gurobiModel->getEnv().set(GRB_DoubleParam_TimeLimit, t);
}

#endif // HAVE_GUROBI
