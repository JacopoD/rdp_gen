import numpy as np
import wse2
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# TODO Ellipse generation: possibility to limit size
# TODO Ellipse generation: find a way to prevent the center of an ellipse to be inside another


def generate_canvas(n_ellipses: int, ellipse_ranges: list, ellipse_ratios: list, ellipse_wse: list,
               wse_factor_background: float = 1, width: int = 500, height: int = 500, n_samples: int = 100, verbose: bool = False):

    assert n_ellipses == len(ellipse_ranges) == len(ellipse_ratios), ""

    for r in ellipse_ratios:
        assert r[0] >= 0 and r[0] <= 1
        assert r[1] >= 0 and r[1] <= 1
        assert r[0] <= r[1]

    assert wse_factor_background > 0 and wse_factor_background <= 1

    for wse in ellipse_wse:
        assert wse > 0 and wse <= 1

    max_x = width
    min_x = 0
    max_y = height
    min_y = 0

    # rng = np.random.default_rng(2022)
    rng = np.random.default_rng()

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
                        existing_test=E, range=ellipse_ranges[i], ratio=ellipse_ratios[i], verbose=verbose)
        E.append(e)
        points_in_ellipse(S, e, i)

    pos = n_sort(S, n_ellipses)

    r = 0
    for i in range(len(pos)):
        if i == 0:
            if verbose:
                print("WSE on background:")
            r += wse2.weighted_sample_elimination(S,
                                                  wse_factor_background, False, 0, pos[i], verbose=verbose)
        else:
            if verbose:
                print("WSE on ellipse {}:".format(i-1))
            r += wse2.weighted_sample_elimination(S,
                                                  ellipse_wse[i-1], False, pos[i-1], pos[i], verbose=verbose)
    if verbose:
        print("{}/{} samples removed".format(r, len(S)))
    # return S, E, canvas
    return S


def gen_ellipse(rng, canvas: tuple, range: tuple, ratio: float, existing_test: list = [], verbose: bool = False):
    
    ok = False
    tries = 0
    max_tries = 10
    while tries < max_tries:
        tries += 1

        radius_x = rng.uniform(range[0], range[1])
        radius_y = radius_x * rng.uniform(ratio[0], ratio[1])

        phi = rng.uniform(0, 2*np.pi)

        c_x = rng.uniform(canvas[0], canvas[1])
        c_y = rng.uniform(canvas[2], canvas[3])

        ok = True
        for e in existing_test:
            if in_ellipse(e, (c_x, c_y)):
                ok = False
                break
        if ok:
            for e in existing_test:
                if in_ellipse((radius_x, radius_y, c_x, c_y, phi), (e[2],e[3])):
                    ok = False
                    break
        
        if verbose and not ok:
            print("Center overlap, try {}/{}".format(tries, max_tries))
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