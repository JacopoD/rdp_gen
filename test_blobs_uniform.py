from random import sample
import my_make_blobs
import matplotlib.pyplot as plt
import matplotlib.patches as patches


samples = [100,200,300,150]
XY, centers, angles, bboxes, ellipses = my_make_blobs.gen_cluster_uniform(samples=samples,
                                        center_box=(-20,20), min_size=5, max_size=15,
                                        weighted_elim=True)

fig, ax = plt.subplots()

for i in range(len(bboxes)):
    ax.add_patch(
                patches.Rectangle((centers[i][0] - bboxes[i][0], centers[i][1] - bboxes[i][1]), bboxes[i][0] * 2, bboxes[i][1] * 2,
                                    edgecolor='red', linestyle='--', facecolor='none')
                )

s = 0
for p in XY:
    s += len(p)
    plt.scatter(p[:, 0], p[:, 1], c="b", marker=".", s=10)
print("{}/{} samples have been removed".format(sum(samples)-s, sum(samples)))

# ax.set_ylim(-10,10)
# ax.set_xlim(-10,10)

plt.show()