import my_make_blobs
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import time


def main():
    test_uniform()


def test_uniform():

    samples = [100, 200, 300, 150]
    start = time.perf_counter()
    XY, centers, angles, bboxes, ellipses = my_make_blobs.gen_cluster_uniform(samples=samples,
                                                                              center_box=(-20, 20), min_size=2, max_size=15,
                                                                              weighted_elim=True)

    end = time.perf_counter()
    fig, ax = plt.subplots()
    button = Button(plt.axes([0.81, 0.000001, 0.1, 0.075]),
                    'Show bbox', hovercolor='0.975')

    R = []
    for i in range(len(bboxes)):
        R.append(patches.Rectangle((centers[i][0] - bboxes[i][0], centers[i][1] - bboxes[i][1]), bboxes[i][0] * 2, bboxes[i][1] * 2,
                                   edgecolor='red', linestyle='--', facecolor='none'))
        R[i].set(visible=False)
        ax.add_patch(R[i])

    s = 0
    for p in XY:
        s += len(p)
        # plt.scatter(p[:, 0], p[:, 1], c="b", marker=".", s=10)
        ax.scatter(p[:, 0], p[:, 1], c="b", marker=".", s=10)
    print("{}/{} samples have been removed. \nThe samples were generated in {} seconds".format(
        sum(samples)-s, sum(samples), end-start))

    # ax.set_ylim(-10,10)
    # ax.set_xlim(-10,10)

    def reset(event):
        # R[0].set(visible=False)
        # for r in R:
        #     print(r)
        #     r.set(visible=True)
        #     # r.remove()
        #     print("A")
        for r in R:
            r.set_visible(not r.get_visible())
        plt.draw()

    button.on_clicked(reset)

    plt.show()


if __name__ == "__main__":
    main()
