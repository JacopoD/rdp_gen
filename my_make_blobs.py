from multiprocessing.sharedctypes import Value
import numpy as np
import numbers
from collections.abc import Iterable
import scipy.spatial as spatial
import miniball
import math
import heapq

# https://github.com/scikit-learn/scikit-learn/blob/37ac6788c/sklearn/datasets/_samples_generator.py#L792


def my_make_blobs(n_samples=100, n_features=2, centers=None, cluster_std=1.0, center_box=(-10.0, 10.0), return_centers=False):

    # Uncomment for reproducible results, NOT WORKING
    # np.random.seed(2022)

    rng = np.random.default_rng(2022)

    if isinstance(n_samples, numbers.Integral):
        if centers is None:
            centers = 3

        if isinstance(centers, numbers.Integral):
            n_centers = centers

            # Uniform distribution
            centers = rng.uniform(
                center_box[0], center_box[1], size=(n_centers, 2))
        else:
            n_features = centers.shape[1]
            n_centers = centers.shape[0]

    # n_samples is an array indicating the numbers of samples per cluster.
    else:
        n_centers = len(n_samples)
        if centers is None:
            centers = rng.uniform(
                center_box[0], center_box[1], size=(n_centers, n_features)
            )
        try:
            assert len(centers) == n_centers
        except TypeError as e:
            raise ValueError(
                "Parameter `centers` must be array-like. Got {!r} instead".format(
                    centers
                )
            ) from e
        except AssertionError as e:
            raise ValueError(
                "Length of `n_samples` not consistent with number of "
                f"centers. Got n_samples = {n_samples} and centers = {centers}"
            ) from e

        else:
            n_features = centers.shape[1]

    # stds: if cluster_std is given as list, it must be consistent
    # with the n_centers
    if hasattr(cluster_std, "__len__") and len(cluster_std) != n_centers:
        raise ValueError(
            "Length of `clusters_std` not consistent with "
            "number of centers. Got centers = {} "
            "and cluster_std = {}".format(centers, cluster_std)
        )

    # If the cluster standard deviation is fixed for all the clusters create an array of the same
    # value repeated len(centers) times i.e. the number of clusters.
    if isinstance(cluster_std, numbers.Real):
        cluster_std = np.full(len(centers), cluster_std)

    X = []
    y = []

    if isinstance(n_samples, Iterable):
        n_samples_per_center = n_samples
    else:
        n_samples_per_center = [(n_samples // n_centers)] * n_centers

        # Add the remainder
        for i in range(n_samples % n_centers):
            n_samples_per_center[i] += 1

    for i in range(len(cluster_std)):
        n = n_samples_per_center[i]
        std = cluster_std[i]
        # Generate array of size n * n_features
        # where n is the number of points and n_features is the number if dimensions in the space (2D,3D,4D,...)
        X.append(rng.normal(loc=centers[i], scale=std, size=(n, n_features)))
        y += [i] * n

    y = np.array(y)

    # X = np.concatenate(X)
    # if return_centers:
    #     return X, y, centers
    # return X, y

    if return_centers:
        return X, y, centers
    return X, y


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
        return "Coords: {}, Weight: {}, Neighbors: {}".format(self.coords, self.weight, len(self.neighbors))


def weighted_sample_elimination(S_np):

    desired = len(S_np) // 2

    # Circle containing all the points in S
    C, r2 = miniball.get_bounding_ball(S_np)
    # print(C, r2)
    c_area = r2 * np.pi

    # Build a kd-tree for samples
    kd = spatial.KDTree(S_np)

    r_max_2d = np.sqrt(c_area/(2*np.sqrt(3)*len(S_np)))

    S = list(map(tuple, S_np))

    for i in range(len(S_np)):
        if S_np[i][0] != S[i][0] or S_np[i][1] != S[i][1]:
            raise ValueError

    samples = dict()

    pq = []

    for i, s in enumerate(S):
        # s_tuple = (s[0], s[1])
        new_s = Sample(coords=s, index=i)
        samples[s] = new_s
        # heapq.heappush(pq, new_s)

    # key == coordinates
    for key in samples:
        s = samples[key]
        neighbors = kd.query_ball_point(s.coords, r_max_2d)
        s.neighbors = neighbors
        # print(neighbors)
        # print(samples[S[neighbors[0]]])
        for n in neighbors:
            d_ij = math.dist(s.coords, S[n])
            d_hat_ij = min(2 * r_max_2d, d_ij)
            # s.weight += np.power(1-(d_hat_ij/2 * r_max_2d), 8)
            s.weight -= np.power(1-(d_hat_ij/2 * r_max_2d), 8)

        heapq.heappush(pq, s)

    while len(pq) > desired:
        s_j = heapq.heappop(pq)

        for s_i in s_j.neighbors:
            s_i_obj = samples[S[s_i]]
            s_i_obj.neighbors.remove(s_j.index)
            # samples[S[s_i]].weight -= s_j.weight

            s_i_obj.weight += s_j.weight

        heapq.heapify(pq)

    return np.array(list(map(lambda x: x.coords, pq)))
