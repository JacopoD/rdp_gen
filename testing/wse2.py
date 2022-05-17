import enum
import numpy as np
from scipy.spatial import KDTree
import heapq
import math
from mec import make_circle


# https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html
# http://www.cemyuksel.com/research/sampleelimination/sampleelimination.pdf

class Sample:
    def __init__(self, coords, neighbors=[], weight=0, index=-1, index_test=-1) -> None:
        self.coords = coords
        self.neighbors = neighbors
        self.weight = weight
        self.index = index
        self.index_test = index_test

    def get_weight(self):
        return self.weight

    def set_weight(self, w):
        self.weight = w

    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __str__(self) -> str:
        return "ID: {} Coords: {}, Weight: {}, Neighbors: {}".format(self.index, self.coords, self.weight, self._print_help())

    def _print_help(self):
        s = ""
        for n in self.neighbors:
            s += str(n)
            s += " "
        return s


def weighted_sample_elimination(S_np: np.ndarray, percentage: float = 1, return_radius: bool = False, start: int = 0, end: int = None):
    """
    Applies weighted sample elimination to the given set of points,
    this algorithm is based on: http://www.cemyuksel.com/research/sampleelimination/sampleelimination.pdf

    Args:

        S_np (list or numpy.ndarray):
            if list, it will be immediately converted to numpy.ndarray

        percentage (int or float): 
            default=1
            percentage of samples that will have weight = 0, number from 0 to 1
    Returns:

        numpy.ndarray: of length len(S_np) // factor, containing the points with lowest weight

    TODO: improve on the data structure holding neighbors in the Sample class, at the moment it's a simple list the problem is that
    TODO:   elements are removed from it which is very expensive. Consider using a set or similar.
    TODO:   Another strategy could be replacing "dead" neighbors with an invalid index such as -1

    """
    if start == end:
        return 0

    if percentage > 1 or percentage < 0:
        raise ValueError

    if end is None:
        end = len(S_np)

    S_np_cut = S_np[start: end]

    # Circle inscribing all the points in S
    # C, r2 = miniball.get_bounding_ball(S_np_cut)

    mec = make_circle(S_np_cut)

    c_area = mec[2] * mec[2] * np.pi

    # Build a kd-tree with the points
    kd = KDTree(S_np_cut)

    r_max_2d = np.sqrt(c_area/(2*np.sqrt(3)*len(S_np_cut)))

    samples = dict()

    pq = []

    j = 0
    for i in range(start, end, 1):
        t = (S_np[i][0], S_np[i][1])
        new_s = Sample(coords=t, index=i, index_test=j)
        samples[t] = new_s
        j += 1

    N = kd.query_ball_tree(kd, r_max_2d)
    no_w_count = 0

    for i in range(start, end, 1):
        s = S_np[i]
        s_obj = samples[(s[0], s[1])]
        s_obj.neighbors = N[i-start]

        for k in range(1, len(N[i-start])):
            n = N[i-start][k]
            d_ij = math.dist(s_obj.coords, S_np[n+start][:2])
            d_hat_ij = min(2 * r_max_2d, d_ij)
            s_obj.weight -= np.power(1-(d_hat_ij/2 * r_max_2d), 8)
        if s_obj.weight == 0:
            no_w_count += 1
        heapq.heappush(pq, s_obj)

    print("{} samples ({}%) have weight 0 before any elimination".format(
        no_w_count, (no_w_count*100)/len(S_np_cut)))

    v = int(percentage * len(S_np_cut)) - no_w_count
    if v < 0:
        v = 0

    print("{} more samples will be removed to reach {}%".format(v, percentage*100))

    removed_count = 0

    for i in range(v):
        s_j = heapq.heappop(pq)

        for k, s_i in enumerate(s_j.neighbors):
            if k == 0:
                continue
            s_i = s_j.neighbors[k] + start
            s = S_np[s_i]
            if (s[0], s[1]) in samples:
                s_i_obj = samples[(s[0], s[1])]
                s_i_obj.neighbors.remove(s_j.index - start)
                s_i_obj.weight += s_j.weight
                if s_i_obj.weight == 0:
                    no_w_count += 1
        del samples[s_j.coords]
        S_np[s_j.index][2] = -2
        removed_count += 1

        heapq.heapify(pq)

    print("{}% of the samples are now with weight = 0\n{} samples have been removed".format(
        percentage*100, removed_count))

    if return_radius:
        return r_max_2d
    return removed_count
