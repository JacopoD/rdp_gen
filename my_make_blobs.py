import numpy as np
import numbers
from collections.abc import Iterable
import scipy.spatial as spatial
from wse import weighted_sample_elimination

# https://github.com/scikit-learn/scikit-learn/blob/37ac6788c/sklearn/datasets/_samples_generator.py#L792


def gen_cluster_normal(n_samples=[100], centers=None, cluster_std=1.0, center_box=(-10.0, 10.0), return_centers=True, wse=False):
    """ 
    Generate normally distributed clusters of points

    Args:

        n_samples (list, optional): List containing the number of samples per cluster. Defaults to [100].
        centers (None or list, optional): List containing the coordinates of the centers of each cluster. Defaults to None.
        cluster_std (float, optional): List containing the standard deviation for each cluster. Defaults to 1.0.
        center_box (tuple, optional): Range in which the centers of the clusters can be genearted. Defaults to (-10.0, 10.0).
        return_centers (bool, optional): If true the coordinates of the centers of the clusters will be returned. Defaults to True.

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:

        XY: ndarray of ndarrays representing the clusters and their points
        (optional) centers: the centers of each cluster
    """

    assert isinstance(n_samples, (list, np.ndarray)
                      ), "Parameter `n_samples` must be list or ndarray"

    # Uncomment for reproducible results
    rng = np.random.default_rng()

    # n_samples is an array indicating the numbers of samples per cluster.
    n_centers = len(n_samples)
    if centers is None:
        centers = rng.uniform(
            center_box[0], center_box[1], size=(n_centers, 2)
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

    XY = []
    # y = []

    # if isinstance(n_samples, Iterable):
    n_samples_per_center = n_samples

    for i in range(len(cluster_std)):
        n = n_samples_per_center[i]
        std = cluster_std[i]
        # Generate array of size n * n_features
        # where n is the number of points and n_features is the number if dimensions in the space (2D,3D,4D,...)
        xy = rng.normal(loc=centers[i], scale=std, size=(n, 2))
        if wse:
            xy = weighted_sample_elimination(xy, 0.95)
        XY.append(xy)

    if return_centers:
        return XY, centers
    return XY


def gen_cluster_uniform(samples=[100], centers=None, center_box=(-5, 5), min_size=0.5, max_size=5, return_centers=True, wse=False):
    """
    Generate uniformly distributed clusters of points enclosed in an ellipse

    Args:

        samples (array-like):
            default=[100]
            the number of samples per cluster

        centers (None or array-like):
            default=None
            the coordinates of centers of the clusters

        center_box (tuple): 
            default=(-5, 5)
            the bounding box for each cluster center

        min_size (number or array-like): default=0.5
            the minimum width or height of the ellipse
            if only one number is specified all the clusters will follow this parameter

        max_size (number or array-like): default=5
            the maximum width or height of the ellipse
            if only one number is specified all the clusters will follow this parameter

        (return_centers : boolean, default=True
        If True, return the coordinates of the centers)

        weighted_elim: boolean, dafault=False
            If True, the weighted sample elimination algorithm will be applied to the samples

    Returns:

        XY (ndarray of ndarray(s)):
            Len(XY) == len(samples)
            the samples generated and filtered

        centers (list of unknown):
            centers of clusters, 
            the inner object depends on user input if centers != None

        angles (list of float): 
            the angles representing the tilt of each ellipse

        bboxes (list of tuples): 
            half width and half height of the bounding box for each ellipse

        ellipses (list of tuples): 
            radius of x and radius of y axis of each ellipse


    TODO : decide if WSE should be applied before or after filtering the points
    """

    if centers is not None and len(centers) != len(samples):
        raise ValueError(
            "Paramenter `centers` must have equal length as parameter `samples`")

    if not isinstance(min_size, Iterable):
        min_size = [min_size] * len(samples)

    if not isinstance(max_size, Iterable):
        max_size = [max_size] * len(samples)

    assert len(max_size) == len(min_size) == len(
        samples), "Parameter `max_size` and `min_size` when provided as array-like must have the same length of paramenter `samples`"

    # rng = np.random.default_rng(2022)
    rng = np.random.default_rng()

    n_centers = len(samples)

    if centers is None:
        # Only 2D generation
        centers = rng.uniform(
            center_box[0], center_box[1], size=(n_centers, 2))

    XY = []
    bboxes = []
    angles = []
    ellipses = []
    # https://stackoverflow.com/questions/87734/how-do-you-calculate-the-axis-aligned-bounding-box-of-an-ellipse
    for i in range(len(samples)):

        radiusX = rng.uniform(min_size[i], max_size[i])
        radiusY = rng.uniform(radiusX, max_size[i])

        phi = rng.uniform(0, 2*np.pi)

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

        # ! Choose a strategy

        # Generate samples --> Removal of points not in ellipse --> Weighted sample elimination
        P = points_in_ellipse(rng.uniform(min_x, max_x, samples[i]), rng.uniform(min_y, max_y, samples[i]),
                              radiusX, radiusY, centers[i][0], centers[i][1], phi)
        if wse:
            P = weighted_sample_elimination(P, 0.9)

        # Generate samples --> Weighted sample elimination --> Removal of points not in ellipse
        # P = np.array(list(zip(rng.uniform(
        #     min_x, max_x, samples[i]), rng.uniform(min_y, max_y, samples[i]))))

        # if wse:
        #     P = weighted_sample_elimination(P, 0.9)

        # P = points_in_ellipse(P[:, 0], P[:, 1], radiusX,
        #                       radiusY, centers[i][0], centers[i][1], phi)

        XY.append(P)
        bboxes.append((bbox_halfwidth, bbox_halfheight))
        angles.append(np.rad2deg(phi))
        ellipses.append((radiusX, radiusY))

    return XY, centers, angles, bboxes, ellipses


# https://stackoverflow.com/questions/7946187/point-and-ellipse-rotated-position-test-algorithm


def points_in_ellipse(Px, Py, a, b, cx, cy, angle):
    """
    Given a list of x,y coordinates and an ellipse,
    computes a list of only the points which are in the ellipse

    Args:

        Px (list): list of x coordinates for the points
        Py (list): list of y coordinates for the points
        a (float): width of the ellipse
        b (float): height of the ellipse
        cx (float): x coordinate of the center of the ellipse
        cy (float): x coordinate of the center of the ellipse
        angle (float): rotation of the ellipse in radians

    Returns:

        ndarray: list of points in the ellipse
    """
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    a2 = a*a
    b2 = b*b

    P = []

    # E = np.power(cos_angle * (Px[0] - cx) + sin_angle * (Py[0] - cy),2) / a2 + \
    #     np.power(sin_angle * (Px[0] - cx) - cos_angle * (Py[0] - cy),2) / b2

    E = np.power(cos_angle * (Px - cx) + sin_angle * (Py - cy), 2) / a2 + \
        np.power(sin_angle * (Px - cx) - cos_angle * (Py - cy), 2) / b2

    for i, e in enumerate(E):
        if e <= 1:
            P.append([Px[i], Py[i]])
    return np.array(P)
