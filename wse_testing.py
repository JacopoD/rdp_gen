import unittest
import wse
import numpy as np
import matplotlib.pyplot as plt

# class Test1(unittest.TestCase):

#     def


def main():
    rng = np.random.default_rng(2022)
    S = rng.normal((0, 0), scale=0.5, size=(20, 2))
    S1, radius = wse.weighted_sample_elimination(S, 1)

    fig, ax = plt.subplots()

    ax.plot(S[:, 0], S[:, 1], ls="", marker="o", color="green")
    ax.plot(S1[:, 0], S1[:, 1], ls="", marker="o")

    for i, c in enumerate(S1):
        ax.annotate(str(i), xy=(c[0], c[1]))
        ax.add_patch(plt.Circle(c, radius, color="orange", fill=False))
    plt.show()

    pass


if __name__ == "__main__":
    main()
