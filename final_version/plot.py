import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import random
from matplotlib.pyplot import figure
import numpy as np
from copy import copy


def plot(S, E, canvas):
    n_ellipses = len(E)
    # S, E, canvas = gen_canvas(n_samples=2000, n_ellipses=n_ellipses)
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()


    # plt.xlim(canvas[0], canvas[1])
    # plt.ylim(canvas[2], canvas[3])

    ax.set_xlim(canvas[0], canvas[1])
    ax.set_ylim(canvas[2], canvas[3])

    ax2.set_xlim(canvas[0], canvas[1])
    ax2.set_ylim(canvas[2], canvas[3])
    

    colors = ["#"+''.join([random.choice('ABCDEF0123456789')
                           for i in range(6)]) for _ in range(n_ellipses)]

    # colors = ["red","green"]

    for s in S:
        ax2.plot(s[0], s[1], c="blue", marker=".", markersize=2)
        if s[2] == -2:
            continue

        if s[2] == -1:
            c = "blue"
        else:
            c = colors[int(s[2])]

        # c = "b"

        ax.plot(s[0], s[1], c=c, marker=".", markersize=2)

    fig2.savefig('/Users/jdv/Desktop/poster_example/NOcolorsNOE.pdf', dpi=120)

    Ep = []
    for e in E:
        a = patches.Ellipse(
            (e[2], e[3]), 2*e[0], 2*e[1], np.rad2deg(e[4]), fill=False)
        # ax.plot(e[2], e[3], c="r", marker=".", markersize=5)
        ax.add_patch(a)
        a2 = patches.Ellipse(
            (e[2], e[3]), 2*e[0], 2*e[1], np.rad2deg(e[4]), fill=False)
        ax2.add_patch(a2)
        Ep.append(a)

    fig.savefig('/Users/jdv/Desktop/poster_example/colors.pdf', dpi=120)
    fig2.savefig('/Users/jdv/Desktop/poster_example/NOcolorsE.pdf', dpi=120)

    button = Button(plt.axes([0.81, 0.000001, 0.1, 0.075]),
                    'Show bbox', hovercolor='0.975')

    def reset(event):
        for e in Ep:
            e.set_visible(not e.get_visible())
        plt.draw()

    button.on_clicked(reset)
    plt.show()
    pass

