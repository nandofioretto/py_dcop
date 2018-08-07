
def takeMin(cost, best_c, i=None, best_i=None):
    if cost < best_c:
        return cost, i
    else:
        return best_c, best_i

def takeMax(cost, best_c, i=None, best_i=None):
    if cost > best_c:
        return cost, i
    else:
        return best_c, best_i

def insertInTuple(_tuple, _pos, _val):
    _tuple_l = list(_tuple)
    _tuple_l[_pos] = _val
    return tuple(_tuple_l)
