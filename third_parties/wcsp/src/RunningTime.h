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

#ifndef RUNNINGTIME_H_
#define RUNNINGTIME_H_

#include <chrono>
#include <memory>

// Manage running time.
class RunningTime
{
private:

    // the starting time when entering the main function
    std::chrono::time_point<std::chrono::high_resolution_clock> starting_time;

    // time limit specified on the command line
    std::chrono::duration<double> time_limit = std::chrono::duration<double>::max();

    RunningTime() {}

public:

    inline void setTimeLimit(const std::chrono::duration<double>& tl) noexcept
    {
        time_limit = tl;
    }

    inline std::chrono::duration<double> getTimeLimit() const noexcept
    {
        return time_limit;
    }

    inline void setStartingTime(
        const std::chrono::time_point<std::chrono::high_resolution_clock>& st) noexcept
    {
        starting_time = st;
    }

    inline std::chrono::duration<double>::rep getCurrentRunningTime()
    {
        using namespace std::chrono;

        return duration_cast<duration<double> >(
            high_resolution_clock::now() - starting_time).count();
    }

    inline bool isTimeOut() const noexcept
    {
        using namespace std::chrono;
        return duration_cast<duration<double> >(high_resolution_clock::now() - starting_time)
            >= time_limit;
    }

    static RunningTime& GetInstance()
    {
        static std::unique_ptr<RunningTime> rt;   // the only RunningTime instance in the world

        if (!rt)   // first time, initialize.
            rt.reset(new RunningTime());

        return *rt;
    }
};

#endif  // RUNNINGTIME_H_
