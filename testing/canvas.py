from turtle import color
import numpy as np
import wse2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import random
from matplotlib.pyplot import figure


# TODO Ellipse generation: possibility to limit size
# TODO Ellipse generation: find a way to prevent the center of an ellipse to be inside another


def gen_canvas(n_ellipses: int, ellipse_ranges: list, ellipse_ratios: list, ellipse_wse: list,
               wse_factor_background: float = 1, width: int = 500, height: int = 500, n_samples: int = 100):

    assert n_ellipses == len(ellipse_ranges) == len(ellipse_ratios), ""

    for r in ellipse_ratios:
        assert r[0] >= 0 and r[0] <= 1
        assert r[1] >= 0 and r[1] <= 1
        assert r[0] <= r[1]

    assert wse_factor_background > 0 and wse_factor_background <= 1

    for wse in ellipse_wse:
        assert wse > 0 and wse <= 1

    # max_x = width / 2
    # min_x = - max_x
    # max_y = height / 2
    # min_y = - max_y

    max_x = width
    min_x = 0
    max_y = height
    min_y = 0

    rng = np.random.default_rng(86541)
    # rng = np.random.default_rng()

    canvas = (min_x, max_x, min_y, max_y)

    S = np.rot90(np.array([rng.uniform(min_x, max_x, n_samples), rng.uniform(
        min_y, max_y, n_samples), np.full(n_samples, -1)]))

    # return S
    E = []

    for i in range(n_ellipses):
        # r = None
        # if ellipse_ranges is not None:
        #     r = ellipse_ranges[i]
        e = gen_ellipse(rng=rng, canvas=canvas,
                        existing_test=E, range=ellipse_ranges[i], ratio=ellipse_ratios[i])
        E.append(e)
        points_in_ellipse(S, e, i)

    pos = n_sort(S, n_ellipses)

    r = 0
    for i in range(len(pos)):
        if i == 0:
            r += wse2.weighted_sample_elimination(S,
                                                  wse_factor_background, False, 0, pos[i])
        else:
            # r += wse2.weighted_sample_elimination(S,
            #                                       ellipse_wse[i-1], False, pos[i-1], pos[i])
            pass
    print("{}/{} samples removed".format(r, len(S)))
    # print("Seed: ", np.random.get_state())
    return S, E, canvas


def gen_ellipse(rng, canvas: tuple, range: tuple, ratio: float, existing_test: list = []):
    # if range is None:
    #     range = (np.sqrt(abs(min(canvas))), abs(min(canvas))/2)
    ok = False
    tries = 0
    while tries < 10 and not ok:
        tries += 1

        # This code can be moved out of the loop if the second approach is used
        # From here
        radius_x = rng.uniform(range[0], range[1])
        # radius_y = rng.uniform(range[0], range[1])
        radius_y = radius_x * rng.uniform(ratio[0], ratio[1])

        phi = rng.uniform(0, 2*np.pi)
        # To here

        c_x = rng.uniform(canvas[0], canvas[1])
        c_y = rng.uniform(canvas[2], canvas[3])

        # if not center_overlap3(E=existing_test, c=(c_x, c_y)):
            # break
        ok = True
        for e in existing_test:
            if in_ellipse(e, (c_x, c_y)):
                ok = False
                print("Center overlap")
                break
        if ok:
            for e in existing_test:
                if in_ellipse((radius_x, radius_y, c_x, c_y, phi), (e[2],e[3])):
                    ok = False
                    print("Center overlap")
                    break
        
        
        # range = (range[0]/2, range[1]/2)

    return (radius_x, radius_y, c_x, c_y, phi)


def in_ellipse(E, p):
    cos_angle = np.cos(E[4])
    sin_angle = np.sin(E[4])

    a2 = E[0]*E[0]
    b2 = E[1]*E[1]
    s_x = p[0]
    s_y = p[1]
    r = np.power(cos_angle * (s_x - E[2]) + sin_angle * (s_y - E[3]), 2) / a2 + \
        np.power(
            sin_angle * (s_x - E[2]) - cos_angle * (s_y - E[3]), 2) / b2

    if r <= 1:
        return True
    return False



def center_overlap3(E, c):

    for ellipse in E:
        cos_angle = np.cos(ellipse[4])
        sin_angle = np.sin(ellipse[4])

        a2 = ellipse[0]*ellipse[0]
        b2 = ellipse[1]*ellipse[1]
        s_x = c[0]
        s_y = c[1]
        r = np.power(cos_angle * (s_x - ellipse[2]) + sin_angle * (s_y - ellipse[3]), 2) / a2 + \
            np.power(
                sin_angle * (s_x - ellipse[2]) - cos_angle * (s_y - ellipse[3]), 2) / b2

        if r <= 1:
            return True
    return False


# def center_overlap(ellipse, S):
#     cos_angle = np.cos(ellipse[4])
#     sin_angle = np.sin(ellipse[4])

#     a2 = ellipse[0]*ellipse[0]
#     b2 = ellipse[1]*ellipse[1]

#     for i in range(len(S)):
#         s_x = S[i][2]
#         s_y = S[i][3]
#         r = np.power(cos_angle * (s_x - ellipse[2]) + sin_angle * (s_y - ellipse[3]), 2) / a2 + \
#             np.power(
#                 sin_angle * (s_x - ellipse[2]) - cos_angle * (s_y - ellipse[3]), 2) / b2

#         if r <= 1:
#             return True
#     return False


def points_in_ellipse(S: np.ndarray, ellipse: tuple, ellipse_id: int):

    cos_angle = np.cos(ellipse[4])
    sin_angle = np.sin(ellipse[4])

    a2 = ellipse[0]*ellipse[0]
    b2 = ellipse[1]*ellipse[1]

    for i in range(len(S)):
        if S[i][2] == -1:
            s_x = S[i][0]
            s_y = S[i][1]
            r = np.power(cos_angle * (s_x - ellipse[2]) + sin_angle * (s_y - ellipse[3]), 2) / a2 + \
                np.power(
                    sin_angle * (s_x - ellipse[2]) - cos_angle * (s_y - ellipse[3]), 2) / b2

            if r <= 1:
                S[i][2] = ellipse_id


# n_id * n, n_id is very small compared to n ==> O(n)
def n_sort(S, n_id):

    i = 0
    pos = []

    for id in range(-1, n_id):
        j = len(S)
        while i < j:
            if not (S[i][2] == id):
                j = j - 1
                S[i][0], S[j][0] = S[j][0], S[i][0]
                S[i][1], S[j][1] = S[j][1], S[i][1]
                S[i][2], S[j][2] = S[j][2], S[i][2]
            else:
                i = i + 1
        i = j
        pos.append(i)
    return pos


def show_canvas(S, E, canvas):
    n_ellipses = len(E)
    # S, E, canvas = gen_canvas(n_samples=2000, n_ellipses=n_ellipses)
    fig, ax = plt.subplots(figsize=(8, 8))

    # fig2, ax2 = plt.subplots(figsize=(8, 8))


    plt.xlim(canvas[0], canvas[1])
    plt.ylim(canvas[2], canvas[3])

    # colors = ["#"+''.join([random.choice('ABCDEF0123456789')
    #                        for i in range(6)]) for _ in range(n_ellipses)]

    colors = ["red","green"]

    for s in S:
        # ax2.plot(s[0], s[1], c="blue", marker=".", markersize=2)
        if s[2] == -2:
            continue

        if s[2] == -1:
            c = "blue"
        else:
            c = colors[int(s[2])]

        # c = "b"

        ax.plot(s[0], s[1], c=c, marker=".", markersize=2)

    Ep = []
    for e in E:
        a = patches.Ellipse(
            (e[2], e[3]), 2*e[0], 2*e[1], np.rad2deg(e[4]), fill=False)
        ax.plot(e[2], e[3], c="r", marker=".", markersize=5)
        ax.add_patch(a)
        Ep.append(a)

    fig.savefig('WSE_SHOW_BG08_ENO.png', dpi=120)

    button = Button(plt.axes([0.81, 0.000001, 0.1, 0.075]),
                    'Show bbox', hovercolor='0.975')

    def reset(event):
        for e in Ep:
            e.set_visible(not e.get_visible())
        plt.draw()

    button.on_clicked(reset)
    plt.show()
    pass