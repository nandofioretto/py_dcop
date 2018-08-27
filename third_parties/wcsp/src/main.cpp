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

#include <iostream>

#include <boost/algorithm/string.hpp>
#include <boost/program_options.hpp>

#include "global.h"
#include "RunningTime.h"
#include "WCSPInstance.h"
#include "ConstraintCompositeGraph.h"
#include "LinearProgramSolverGurobi.h"
#include "MWVCSolverLinearProgramming.h"
#include "MWVCSolverMessagePassing.h"
#include "KernelizerLinearProgramming.h"

template <class T1, class T2>
static void print_results(const T1& instance, const T2& assignments)
{
    auto opt_value = instance.computeTotalWeight(assignments);

    if (RunningTime::GetInstance().isTimeOut())
        std::cout << "Timeout solution" << std::endl;
    std::cout << "Best assignments:" << std::endl;
    std::cout << "ID\tassignment" << std::endl;
    for (const auto& v : assignments)
    {
        std::cout << v.first << '\t' << v.second << std::endl;
    }
    std::cout << "Optimal value: " << opt_value << std::endl;
}

int main(int argc, const char** argv)
{
    RunningTime::GetInstance().setStartingTime(std::chrono::high_resolution_clock::now());

    // Parsing command line arguments and print the help message if needed
    namespace po = boost::program_options;
    po::variables_map vm;
    char mwvc_solver;
    double eps, delta, delta1;
    std::string ccg_out_file;
    std::string parameters;  // parameters of some MWVC solvers
    char file_format;
    double time_limit;
    {
        po::options_description desc("Options");
        desc.add_options()
            ("help,h", "print help message")
            ("ccg,c", po::value<>(&ccg_out_file)->default_value(""),
             "specify the file that the output CCG should be written into (default is stdout)")
            ("file-format,f", po::value<>(&file_format)->default_value('d')->notifier(
                [](char x){
                    if (x != 'd' && x != 'u')
                        throw po::validation_error(
                            po::validation_error::invalid_option_value,
                            "file-format", std::string(1, x));
                }),
             "specify the input file format:\n"
             "d: DIMACS\n"
             "u: UAI\n")
            ("ccg-only,g", "print the CCG only without solving the MWVC problem on it")
            ("no-kernelization,k", "don't kernelize")
            ("kernelization-only,K", "exit after kernelization")
#if 0
            ("message-passing,M", "do message passing on the original problem directly")
#endif
            ("linear-programming,L", "use linear programming to solve the original problem directly")
            ("mwvc-solver,m", po::value<>(&mwvc_solver)->default_value('l')->notifier(
                [](char x){
                    if (std::string("lcsatxm").find(x) == std::string::npos)
                        throw po::validation_error(
                            po::validation_error::invalid_option_value,
                            "mwvc-solver", std::string(1, x));
                }),
             "MWVC solver:\n"
             "l: linear program solver\n"
             "m: Message Passing\n")
            ("parameters,p", po::value<>(&parameters)->default_value(""))
            ("time-limit,t",
             po::value<double>(&time_limit)->default_value(std::numeric_limits<double>::max()),
             "specify the time limit in seconds (currently used for message passing and linear programming algorithms)");

        po::options_description desc_hidden("Hidden Options");
        desc_hidden.add_options()
            ("input-file", po::value<std::string>()->required(), "specify input file");

        po::positional_options_description desc_p;
        desc_p.add("input-file", 1);

        po::options_description all_options("Options");
        all_options.add(desc).add(desc_hidden);
        try
        {
            po::store(po::command_line_parser(argc, argv).
                      options(all_options).positional(desc_p).run(), vm);

            if (vm.count("help"))  // print help message
            {
                std::cerr << "Usage: " << argv[0] << " [options] [input-file]" << std::endl;
                std::cerr << desc << std::endl;
                return 1;
            }

            if (vm.count("input-file") != 1)
                throw po::error_with_no_option_name("An input file must be specified.");

            po::notify(vm);

            // validate p
            if (mwvc_solver == 'a')
            {
                std::vector<std::string> p;
                boost::split(p, parameters, boost::is_any_of(","));
                if (p.size() != 3)
                    throw po::validation_error(
                        po::validation_error::invalid_option_value, "parameters",
                        "3 parameters (epsilon, delta, delta1) separated with commas are expected.");
                eps = std::stod(p.at(0));
                delta = std::stod(p.at(1));
                delta1 = std::stod(p.at(2));

            }
        }
        catch (const std::exception& e)
        {
            std::cerr << e.what() << std::endl;
            std::cerr << "Run this program with the \"--help\" option to see help." << std::endl;
            return 1;
        }
    }

    std::ifstream in(vm["input-file"].as<std::string>());

    if (!in)
    {
        std::cerr << "Unable to read file \"" <<
            vm["input-file"].as<std::string>() << '"'<< std::endl;
        return 2;
    }

    WCSPInstance<>::Format fformat;
    switch (file_format)
    {
    case 'd':
        fformat = WCSPInstance<>::Format::DIMACS;
        break;
    case 'u':
        fformat = WCSPInstance<>::Format::UAI;
        break;
    }
    WCSPInstance<> instance(in, fformat);
    instance.displayNonBooleanVariableMapping();

    if (time_limit != std::numeric_limits<double>::max())  // time limit is set
        RunningTime::GetInstance().setTimeLimit(std::chrono::duration<double>(time_limit));

#if 0
    if (vm.count("message-passing"))
    {
        std::map<WCSPInstance<>::variable_id_t, bool> assignments =
            instance.solveUsingMessagePassing(1e-6);
        print_results(instance, assignments);
        return 0;
    }
#endif

    if (vm.count("linear-programming"))
    {
        LinearProgramSolverGurobi lps;
        auto solution = instance.solveUsingLinearProgramming(lps);
        print_results(instance, solution);
        return 0;
    }

    ConstraintCompositeGraph<> ccg;

    WCSPInstance<>::constraint_t::Polynomial p;
    for (const auto& c : instance.getConstraints())
        c.toPolynomial(p);
    // s is the remnant weight
    ConstraintCompositeGraph<>::weight_t s = ccg.addPolynomial(p);
    ccg.addCliques(instance.getNonBooleanVariables());

    // The reason that we use a map instead of a set to represent the vertex cover is that after
    // each step, we can see what variables have been assigned and what have not.
    std::map<ConstraintCompositeGraph<>::variable_id_t, bool> assignments;

    ccg.simplify(assignments);
    std::cout << "==========================" << std::endl;
    std::cout << "Variables simplified out: " << assignments.size() << std::endl;
    std::cout << "==========================" << std::endl;
    auto stats = ccg.getStatistics();
    std::cout << "==========================" << std::endl;
    std::cout << "Number of variables: " << stats[0] << std::endl;
    std::cout << "Number of type 1 auxiliary variables: " << stats[1] << std::endl;
    std::cout << "Number of type 2 auxiliary variables: " << stats[2] << std::endl;
    std::cout << "==========================" << std::endl;
    // std::cout << ccg << std::endl;
    ccg.toDimacs(std::cout, true);
    if (!ccg_out_file.empty())
    {
        std::ofstream ofs(ccg_out_file);
        if (!ofs)
        {
            std::cerr << "Failed to open file \"" << ccg_out_file << '"' << std::endl;
            abort();
        }
        ofs.exceptions(std::ofstream::failbit | std::ofstream::badbit);
        ccg.toDimacs(ofs, true);
    }

    std::cerr << std::setprecision(std::numeric_limits<decltype(s)>::digits10 + 1) <<
        "s = " << s << std::endl;

    if (vm.count("ccg-only"))   // don't solve the MWVC problem
        return 0;

    do {
        auto g = *ccg.getGraph();
        if (vm.count("no-kernelization"))
            std::cout << "================================" << std::endl <<
                         "|| No kernelization performed ||" << std::endl <<
                         "================================" << std::endl;
        else
        {
            size_t cur_assignment_size = -1;

            for (size_t i = 1; cur_assignment_size != assignments.size(); ++ i)
            {
                cur_assignment_size = assignments.size();

                KernelizerLinearProgramming<> klp(new LinearProgramSolverGurobi());
                klp.kernelize(g, assignments);
                std::cout << "==========================" << std::endl;
                std::cout << "After the " << i <<
                    "th kernelization, number of variables resolved: " <<
                    assignments.size() << std::endl;
                std::cout << "After the " << i << "th kernelization, number of variables left: " <<
                    ccg.getNumberOfVariables() - assignments.size() << std::endl;
                std::cout << "==========================" << std::endl;

                // Don't continue if all variables have been factored out.
                if (assignments.size() >= ccg.getNumberOfVariables())
                    break;
            }

            if (assignments.size() >= ccg.getNumberOfVariables())
                break;
        }

        if (vm.count("kernelization-only"))
            std::exit(0);

        switch (mwvc_solver)
        {
        case 'l':
        {
            MWVCSolverLinearProgramming<> mslp(new LinearProgramSolverGurobi());
            mslp.solve(g, assignments, instance);
            break;
        }
        case 'm':
        {
            MWVCSolverMessagePassing<> msmp(1e-6);
            msmp.solve(g, assignments, instance);
            break;
        }
        }
    } while(0);

    std::cout << "=================================================" << std::endl;

    std::map<WCSPInstance<>::variable_id_t, WCSPInstance<>::non_boolean_value_t> solution;
    for (WCSPInstance<>::variable_id_t v = 0; v < instance.getNonBooleanVariables().size(); ++ v)
    {
        const auto& bvs = instance.getNonBooleanVariables()[v];

        // no assignment specified for bvs[0], which mean it can be any value (e.g., not in the
        // WCSP). No need to modify solution.
        if (assignments.count(bvs[0]) == 0)
            continue;

        if (bvs.size() == 1)
        {
            solution[v] = assignments.at(bvs[0]);
            continue;
        }

        auto false_v = std::find_if_not(
            bvs.begin(), bvs.end(),
            [&](ConstraintCompositeGraph<>::variable_id_t id){return assignments.at(id);});

        if (false_v == bvs.end())  // No variable is false
            solution[v] = 0;
        else
            solution[v] = std::distance(bvs.begin(), false_v) + 1;
    }

    print_results(instance, solution);

    return 0;
}
