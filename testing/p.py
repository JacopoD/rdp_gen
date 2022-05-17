from PIL import Image, ImageDraw
from canvas import gen_canvas, show_canvas


CANVAS_X = 1000
CANVAS_Y = 1000

GEN_CANVAS_X = 30
GEN_CANVAS_Y = 30

i = Image.new("RGB", (CANVAS_X, CANVAS_Y), "white")

S, E, canvas = gen_canvas(
    width=GEN_CANVAS_X, height=GEN_CANVAS_Y, n_samples=350, n_ellipses=5,
    ellipse_ranges=[(5, 10), (2, 7), (2, 3), (4, 7), (2, 5)],
    ellipse_ratios=[(0.6, 0.8), (0.9, 1), (0.3, 0.8),(0.3, 0.8),(0.3, 0.8)],
    wse_factor_background=1,
    ellipse_wse=[0.2, 0.7, 0.3, 0.5, 0.8]
)

# S, E, canvas = gen_canvas(
#     width=500, height=500, n_samples=3000, n_ellipses=0,
#     ellipse_ranges=[],
#     ellipse_ratios=[],
#     wse_factor_background=1,
#     ellipse_wse=[]
# )


draw = ImageDraw.Draw(i)

count = 0
for s in S:
    if s[2] == -2:
        continue
    count += 1

    p_scaled = [round(s[0] * CANVAS_X / GEN_CANVAS_X), round(s[1] * CANVAS_Y / GEN_CANVAS_Y)]
    # p_scaled = (round(p_scaled[0])+CANVAS_X//2, abs((round(p_scaled[1])+CANVAS_Y//2)-CANVAS_Y))
    if p_scaled[0] >= CANVAS_X or p_scaled[0] < 0 or p_scaled[1] >= CANVAS_Y or p_scaled[1] < 0:
        print("Error")
    # draw.point(p, fill="blue")
    # print("{},{} --> {},{}".format(s[0],s[1],p_scaled[0],p_scaled[1]))
    # print(p_scaled)

    draw.point(p_scaled, fill="blue")


# draw.point((0, 0), fill="black")
# draw.point((250, 250), fill="violet")
# draw.point((490, 490), fill="black")
i.show()

# S, E, canvas = gen_canvas(width=500, height=500, n_samples=1000, n_ellipses=2)
show_canvas(S, E, canvas)
