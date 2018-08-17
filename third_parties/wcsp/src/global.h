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

#ifndef GLOBAL_H_
#define GLOBAL_H_

// used to simulate the python "with"
#define WITH(x) x

// self increment of 1 for bitset
template <typename T>
void bitset_increase_1(T& b)
{
    for (size_t i = 0; i < b.size(); ++ i)
    {
        if (b[i])
            b[i] = 0;
        else
        {
            b[i] = 1;
            break;
        }
    }
}

#endif // GLOBAL_H_
