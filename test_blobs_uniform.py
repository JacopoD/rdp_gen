import my_make_blobs
import matplotlib.pyplot as plt
import matplotlib.patches as patches

e_dim, phi, center, XY, h_width, h_height = my_make_blobs.gen_cluster_uniform(weighted_elim=True)

r = patches.Rectangle((center[0] - h_width, center[1] - h_height), h_width*2, h_height*2,
                        edgecolor='red', linestyle='--', facecolor='none')
fig, ax = plt.subplots()
ax.add_patch(r)

plt.scatter(XY[:, 0], XY[:, 1], c="b", marker=".", s=10)

ax.set_ylim(-10,10)
ax.set_xlim(-10,10)

plt.show()