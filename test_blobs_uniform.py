import my_make_blobs
import matplotlib.pyplot as plt
import matplotlib.patches as patches

XY, centers, angles, bboxes, ellipses = my_make_blobs.gen_cluster_uniform(samples=[100,200,300],weighted_elim=True)

fig, ax = plt.subplots()

for i in range(len(bboxes)):
    ax.add_patch(
                patches.Rectangle((centers[i][0] - bboxes[i][0], centers[i][1] - bboxes[i][1]), bboxes[i][0] * 2, bboxes[i][1] * 2,
                                    edgecolor='red', linestyle='--', facecolor='none')
                )
for p in XY:
    plt.scatter(p[:, 0], p[:, 1], c="b", marker=".", s=10)

# ax.set_ylim(-10,10)
# ax.set_xlim(-10,10)

plt.show()