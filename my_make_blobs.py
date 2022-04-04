import numpy as np
import numbers
from collections.abc import Iterable
import scipy.spatial as spatial
import miniball
import math
import heapq

# https://github.com/scikit-learn/scikit-learn/blob/37ac6788c/sklearn/datasets/_samples_generator.py#L792

# Distribution:
# 0 for normal
# 1 for uniform
def gen_cluster_normal(n_samples=100, n_features=2, centers=None, cluster_std=1.0, center_box=(-10.0, 10.0), return_centers=True):

    # Uncomment for reproducible results
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

    if not isinstance(S_np, np.ndarray):
        S_np = np.array(S_np)

    desired = len(S_np) // 1.5

    # Circle containing all the points in S
    C, r2 = miniball.get_bounding_ball(S_np)
    # print(C, r2)
    c_area = r2 * np.pi

    # Build a kd-tree with the points
    kd = spatial.KDTree(S_np)

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

# Center box, the range in which the ellipses can be centered
def gen_cluster_uniform(samples=[100], centers=None, center_box=(-5, 5), min_size=0.5, max_size=5, return_centers=True, weighted_elim=False):
    # rng = np.random.default_rng(2022)
    rng = np.random.default_rng()

    n_centers = len(samples)
    if centers is not None and len(centers) != len(samples):
        raise ValueError("If provided, len(centers) must be equal to len(samples)")
    if centers is None:
        # Only 2D generation
        centers = rng.uniform(center_box[0], center_box[1], size=(n_centers, 2))

    XY = []
    bboxes = []
    angles = []
    ellipses = []
    # https://stackoverflow.com/questions/87734/how-do-you-calculate-the-axis-aligned-bounding-box-of-an-ellipse
    for i in range(len(samples)):

        radiusX = rng.uniform(min_size,max_size)
        radiusY = rng.uniform(radiusX, max_size)

        phi = rng.uniform(0,2*np.pi)

        radians90 = phi + np.pi / 2

        ux = radiusX * np.cos(phi)
        uy = radiusX * np.sin(phi)
        vx = radiusY * np.cos(radians90)
        vy = radiusY * np.sin(radians90)

        bbox_halfwidth = np.sqrt(ux * ux + vx * vx)
        bbox_halfheight = np.sqrt(uy * uy + vy * vy)
        min_x = centers[i][0] - bbox_halfwidth
        min_y = centers[i][1] - bbox_halfheight

        max_x = centers[i][0] + bbox_halfwidth
        max_y = centers[i][1] + bbox_halfheight


        P = points_in_ellipse(rng.uniform(min_x, max_x, samples[i]),rng.uniform(min_y, max_y, samples[i]), \
                                radiusX, radiusY, centers[i][0], centers[i][1], phi)
        if weighted_elim:
            P = weighted_sample_elimination(P)

        XY.append(P)
        bboxes.append((bbox_halfwidth, bbox_halfheight))
        angles.append(np.rad2deg(phi))
        ellipses.append((radiusX, radiusY))


        # return [radiusX,radiusY], np.rad2deg(phi), centers[i], XY, bbox_halfwidth, bbox_halfheight
    return XY, centers, angles, bboxes, ellipses

# https://stackoverflow.com/questions/7946187/point-and-ellipse-rotated-position-test-algorithm
def points_in_ellipse(Px, Py, a, b, cx, cy, angle):

    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    a2 = a*a
    b2 = b*b

    P = []

    # E = np.power(cos_angle * (Px[0] - cx) + sin_angle * (Py[0] - cy),2) / a2 + \
    #     np.power(sin_angle * (Px[0] - cx) - cos_angle * (Py[0] - cy),2) / b2

    E = np.power(cos_angle * (Px - cx) + sin_angle * (Py - cy),2) / a2 + \
        np.power(sin_angle * (Px - cx) - cos_angle * (Py - cy),2) / b2
    
    for i, e in enumerate(E):
        if e <= 1:
            P.append([Px[i],Py[i]])
    return np.array(P)