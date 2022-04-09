import my_make_blobs
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import numpy as np
import time
from matplotlib.widgets import Button


def main():
    test_my_blobs()


def test_my_blobs():

    samples = [20, 200, 300, 150]
    cluster_std = [0.2, 0.5, 0.8, 0.7]
    start = time.perf_counter()

    X, centers = my_make_blobs.gen_cluster_normal(
        samples, centers=None,  cluster_std=cluster_std,
        center_box=(-0.0, 10.0), return_centers=True, wse=True
    )
    end = time.perf_counter()

    n_components = len(X)

    fig, ax = plt.subplots()

    colors = ["#"+''.join([random.choice('ABCDEF0123456789')
                           for i in range(6)]) for _ in range(n_components)]

    for k, col in enumerate(colors):
        plt.scatter(X[k][:, 0], X[k][:, 1], c=col, marker=".", s=10)

    # plt.scatter(centers[:, 0], centers[:, 1], c="b", s=50)
    s = 0
    C = []
    for j in range(len(X)):
        s += len(X[j])
        C.append(confidence_ellipse(X[j], centers[j]))
        ax.add_patch(C[j])

    print("=============\n{}/{} samples have been removed. \nThe samples were generated in {} seconds".format(
        sum(samples)-s, sum(samples), end-start))

    button = Button(plt.axes([0.81, 0.000001, 0.1, 0.075]),
                    'Show conf ell', hovercolor='0.975')

    def reset(event):
        for c in C:
            c.set_visible(not c.get_visible())
        plt.draw()

    button.on_clicked(reset)

    plt.title("My Blobs")
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

    # print("Eigenvectors: \n{}\n Eigenvalues: \n{}\n".format(eigenvec, eigenval))

    # print("Max eigenval: {}".format(max_eigenval))
    # print("Min eigenval: {}".format(min_eigenval))

    max_eigenvec_ind_c = 0
    max_eigenval = eigenval[0][0]
    for r in range(len(eigenval)):
        for c in range(len(eigenval[0])):
            if abs(eigenval[r][c]) >= max_eigenval:
                max_eigenvec_ind_c = c
                max_eigenval = eigenval[r][c]

    # print("Max eigenvector in eigenvectors matrix (column): {}".format(
    #     max_eigenvec_ind_c))

    max_eigenvec = eigenvec[:, max_eigenvec_ind_c]

    # print("Max eigenvector: {}".format(max_eigenvec))

    if(max_eigenvec_ind_c == 0):
        min_eigenvec = eigenvec[:, 1]
    else:
        min_eigenvec = eigenvec[0, :]

    # print("Min eigenvector: ", min_eigenvec)

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

    # print("Theta: ", angle)

    theta = np.degrees(angle)

    e = patches.Ellipse((center[0], center[1]), width=a, height=b, angle=theta,
                        edgecolor='blue', linestyle='--', facecolor='none')

    return e


if __name__ == "__main__":
    main()
