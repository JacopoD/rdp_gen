import numpy as np
import miniball
from scipy.spatial import KDTree
import heapq
import math


# https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html
# http://www.cemyuksel.com/research/sampleelimination/sampleelimination.pdf
# https://pypi.org/project/miniball/

class Sample:
    def __init__(self, coords, neighbors=[], weight=0, index=-1) -> None:
        self.coords = coords
        self.neighbors = neighbors
        self.weight = weight
        self.index = index

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


def weighted_sample_elimination(S_np, percentage=1):
    """
    Applies weighted sample elimination to the given set of points,
    this algorithm is based on: http://www.cemyuksel.com/research/sampleelimination/sampleelimination.pdf

    The percentage of samples removed is not guaranteed, the elimination process stops when the highest weight is == 0
    If more samples than what it will take to reach max weight == 0 
    If max weight == 0 is reached before the specified amount of samples is eliminated the output will not be int(len(S_np)*(1-percentage))
    Args:

        S_np (list or numpy.ndarray):
            if list, it will be immediately converted to numpy.ndarray

        percentage (int or float): 
            default=1
            percentage of samples that will have no neighbors, number from 0 to 1
    Returns:

        numpy.ndarray: of length len(S_np) // factor, containing the points with lowest weight

    TODO: In case max W == 0 is reached before the specified amount of samples is reached add the possibility to randomly remove samples

    """

    if percentage > 1 or percentage < 0:
        raise ValueError

    if not isinstance(S_np, np.ndarray):
        S_np = np.array(S_np)

    # Circle inscribing all the points in S
    C, r2 = miniball.get_bounding_ball(S_np)
    # print(C, r2)
    c_area = r2 * np.pi

    # Build a kd-tree with the points
    kd = KDTree(S_np)

    r_max_2d = np.sqrt(c_area/(2*np.sqrt(3)*len(S_np)))

    # Tuples are hashable, np arrays are not
    S = list(map(tuple, S_np))

    samples = dict()

    pq = []

    for i, s in enumerate(S):
        # s_tuple = (s[0], s[1])
        new_s = Sample(coords=s, index=i)
        samples[s] = new_s
        # heapq.heappush(pq, new_s)

    N = kd.query_ball_tree(kd, r_max_2d)
    no_w_count = 0

    for i, s in enumerate(S):
        s_obj = samples[s]
        s_obj.neighbors = N[i]
        for k, n in enumerate(N[i]):
            if k == 0:
                continue
            d_ij = math.dist(s_obj.coords, S[n])
            d_hat_ij = min(2 * r_max_2d, d_ij)
            s_obj.weight -= np.power(1-(d_hat_ij/2 * r_max_2d), 8)
        if s_obj.weight == 0:
            no_w_count += 1
        heapq.heappush(pq, s_obj)

    # for key in samples:
    #     print(samples[key])

    # for e in pq:
        # print(samples[e])

    v = int(percentage * len(S))

    while no_w_count > v:
        s_j = heapq.heappop(pq)
        if s_j.weight == 0:
            break

        for i, s_i in enumerate(s_j.neighbors):
            if i == 0:
                continue
            if S[s_i] in samples:
                s_i_obj = samples[S[s_i]]
                s_i_obj.neighbors.remove(s_j.index)
                s_i_obj.weight += s_j.weight
                # print(s_i_obj)
                if s_i_obj.weight == 0:
                    no_w_count += 1
        del samples[s_j.coords]
        heapq.heapify(pq)

    for key in samples:
        print(samples[key])

    print(no_w_count, len(samples))

    return np.array(list(map(lambda x: samples[x].coords, samples))), r_max_2d

    # return np.array(list(map(lambda x: x.coords, pq)))