import numpy as np
from PIL import Image, ImageDraw


CANVAS_X = 500
CANVAS_Y = 500

def main():
    i = Image.new("RGB", (CANVAS_X, CANVAS_Y), "white")

    rng = np.random.default_rng(2022)
    P = [rng.uniform(0, 10, 3), rng.uniform(
        0, 10, 3)]
    print(P)
    PT = []

    # for p in P:
    #     pt = [p[0] * CANVAS_X / 10, p[1] * CANVAS_Y / 10]
    #     PT.append(pt)
    draw = ImageDraw.Draw(i)

    for p in zip(P[0],P[1]):
        draw.point(p, fill="red")
        pt = [round(p[0] * CANVAS_X / 10), round(p[1] * CANVAS_Y / 10)]
        PT.append(pt)
    
    # print(PT)
    for p in PT:
        print(p)
        draw.point(p, fill="blue")
        print((round(p[0])+CANVAS_X//2, abs((round(p[1])+CANVAS_Y//2)-CANVAS_Y)))
        draw.point((round(p[0])+CANVAS_X//2, abs((round(p[1])+CANVAS_Y//2)-CANVAS_Y)), fill="orange")
    i.show()
    pass


if __name__ == "__main__":
    main()