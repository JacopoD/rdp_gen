import my_make_blobs
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import numpy as np


def main():
    test_my_blobs()


def test_my_blobs():

    samples = [20, 200, 300, 150]

    X, centers = my_make_blobs.gen_cluster_normal(
        samples, centers=None,  cluster_std=[0.2, 0.5, 0.8, 0.7],
        center_box=(-0.0, 10.0), return_centers=True
    )

    n_components = len(samples)

    fig, ax = plt.subplots()

    colors = ["#"+''.join([random.choice('ABCDEF0123456789')
                           for i in range(6)]) for _ in range(n_components)]

    for i in range(len(X)):
        X[i] = my_make_blobs.weighted_sample_elimination(X[i], 0.95)

    for k, col in enumerate(colors):
        plt.scatter(X[k][:, 0], X[k][:, 1], c=col, marker=".", s=10)

    plt.scatter(centers[:, 0], centers[:, 1], c="b", s=50)

    for j in range(len(X)):
        ax.add_patch(confidence_ellipse(X[j], centers[j]))

    plt.title("My Blobs")
    # plt.xticks([])
    # plt.yticks([])
    plt.show()

# http://www.cs.utah.edu/~tch/CS6640F2020/resources/How%20to%20draw%20a%20covariance%20error%20ellipse.pdf


def confidence_ellipse(X, center):
    x = X[:, 0]
    y = X[:, 1]
    cov = np.cov(x, y)

    eigenval, eigenvec = np.linalg.eig(cov)

    max_eigenval = np.max(eigenval)
    min_eigenval = np.min(eigenval)

    eigenval = np.array([[eigenval[0], 0], [0, eigenval[1]]])

    print("Eigenvectors: \n{}\n Eigenvalues: \n{}\n".format(eigenvec, eigenval))

    print("Max eigenval: {}".format(max_eigenval))
    print("Min eigenval: {}".format(min_eigenval))

    max_eigenvec_ind_c = 0
    max_eigenval = eigenval[0][0]
    for r in range(len(eigenval)):
        for c in range(len(eigenval[0])):
            if abs(eigenval[r][c]) >= max_eigenval:
                max_eigenvec_ind_c = c
                max_eigenval = eigenval[r][c]

    print("Max eigenvector in eigenvectors matrix (column): {}".format(
        max_eigenvec_ind_c))

    max_eigenvec = eigenvec[:, max_eigenvec_ind_c]

    print("Max eigenvector: {}".format(max_eigenvec))

    if(max_eigenvec_ind_c == 0):
        min_eigenvec = eigenvec[:, 1]
    else:
        min_eigenvec = eigenvec[0, :]

    print("Min eigenvector: ", min_eigenvec)

    angle = np.arctan2(max_eigenvec[1], max_eigenvec[0])

    if angle < 0:
        angle = angle + 2 * np.pi

    # https://www.scribbr.com/statistics/standard-deviation/#:~:text=the%20empirical%20rule%3F-,The%20empirical%20rule%2C%20or%20the%2068%2D95%2D99.7%20rule,standard%20deviations%20of%20the%20mean.
    # Number of standard deviations of the mean.
    # ~68% within 1 std of the mean
    # ~95% within 2 std of the mean
    # ~99.7% within 3 std of the mean
    n_std = 2

    a = np.sqrt(max_eigenval) * n_std * 2
    b = np.sqrt(min_eigenval) * n_std * 2

    print("Theta: ", angle)

    theta = np.degrees(angle)

    e = patches.Ellipse((center[0], center[1]), width=a, height=b, angle=theta,
                        edgecolor='blue', linestyle='--', facecolor='none')

    return e


if __name__ == "__main__":
    main()
