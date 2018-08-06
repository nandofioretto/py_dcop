
def take_min(cost, best_c, i=None, best_i=None):
    if cost < best_c:
        return cost, i
    else:
        return best_c, best_i

def take_max(cost, best_c, i=None, best_i=None):
    if cost > best_c:
        return cost, i
    else:
        return best_c, best_i