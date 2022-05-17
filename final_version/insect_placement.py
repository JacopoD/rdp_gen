from PIL import Image, ImageDraw
from canvas import generate_canvas
import random

def main():

    CANVAS_X = 1000
    CANVAS_Y = 1000


    # % di canvas_X invece che un numero fisso
    GEN_CANVAS_X = 30
    # % di canvas_Y invece che un numero fisso
    GEN_CANVAS_Y = 30

    i = Image.new("RGB", (CANVAS_X, CANVAS_Y), "white")

    S, E, canvas = generate_canvas(
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

    insect = Image.open("/Users/jdv/Desktop/bachelor_projects/Desktop/obj_insects/20_frankliniella.png")

    insect_resized = resize_pic(insect, 60)

    # angles = [0,90,180,270]

    count = 0
    for s in S:
        if s[2] == -2:
            continue
        count += 1

        p_scaled = [round(s[0] * CANVAS_X / GEN_CANVAS_X), round(s[1] * CANVAS_Y / GEN_CANVAS_Y)]
        if p_scaled[0] >= CANVAS_X or p_scaled[0] < 0 or p_scaled[1] >= CANVAS_Y or p_scaled[1] < 0:
            print("Error")

        # insect_resized = insect_resized.rotate(angles[random.randint(0,3)], resample=Image.BICUBIC)
        i2 = insect_resized.rotate(random.randint(0,360), resample=Image.BICUBIC)
        i.paste(i2, p_scaled, i2)

    i.show()

    # show_canvas(S, E, canvas)



# https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
def resize_pic(img, basewidth):
    wpercent = (basewidth/float(img.size[0]))
    hsize = int(float(img.size[1])*float(wpercent))
    img = img.resize(size=(basewidth,hsize))
    return img


if __name__ == "__main__":
    main()
