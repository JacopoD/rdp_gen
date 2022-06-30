import os
import sys
from PIL import Image
import random
from canvas import generate_canvas
from time import time
import numpy as np
import plot

def generate_img(config):
    canvas = (1000,1000)
    if config["background_path"] == None:
        img = Image.new("RGB", (canvas[0], canvas[1]), "white")
    else:
        img = Image.open(config["background_path"])
        canvas = img.size
    if config["verbose"]:
        print("Background image size: {}".format(canvas))


    if config["overlays_scaling"] is None:
        config["overlays_scaling"] = 0.05

    overlays = load_images(config["overlays_path"], config, config["verbose"])

    for i in range(len(overlays)):
        overlays[i] = resize_pic(overlays[i], round(canvas[0] * config["overlays_scaling"]))

    generation_canvas_scaling = 0.03

    generation_canvas = (round(canvas[0]* generation_canvas_scaling),round(canvas[1]* generation_canvas_scaling))

    if config["verbose"]:
        print("Generation canvas size: {}".format(generation_canvas))


    rng = np.random.default_rng()

    if config["ellipses_wse"] is None:
        # config["ellipses_wse"] = rng.uniform(0.75,0.95,config["n_clusters"])
        config["ellipses_wse"] = rng.uniform(0.05,1,config["n_clusters"])

    if config["wse_background"] is None:
        config["wse_background"] = rng.uniform(max(config["ellipses_wse"]),1)

    if config["ellipse_ranges"] is None:
        config["ellipse_ranges"] = [np.sort(rng.uniform(min(generation_canvas)/2, max(generation_canvas)/2, 2))]  * config["n_clusters"]

    if config["ellipse_ratios"] is None:
        config["ellipse_ratios"] = [np.sort(rng.uniform(0.2, 0.9, 2))] * config["n_clusters"]

    S, E, c, removed_count = generate_canvas(
        width=generation_canvas[0],
        height=generation_canvas[1],
        n_samples=config["n_samples"], 
        n_ellipses=config["n_clusters"],
        ellipse_ranges=config["ellipse_ranges"],
        ellipse_ratios=config["ellipse_ratios"],
        wse_factor_background=config["wse_background"],
        ellipse_wse=config["ellipses_wse"],
        verbose=config["verbose"]
    )

    pasted = 0

    for s in S:
        if s[2] == -2:
            continue
        p_scaled = [round(s[0] * canvas[0] / generation_canvas[0]), round(s[1] * canvas[1] / generation_canvas[1])]
        # print("{},{} --> {},{}".format(s[0],s[1],p_scaled[0],p_scaled[1]))
        i = random.randint(0, config["overlay_n"]-1)
        ov = overlays[i].rotate(random.randint(0,360), resample=Image.Resampling.BICUBIC, expand = True)
        
        if fits(ov, img, p_scaled):
            pasted += 1
            # trans_paste(ov, img, box=p_scaled, alpha=0)
            img.paste(ov, p_scaled, ov)

    if config["verbose"]:
        print("{}/{} samples fit on the final image".format(pasted, config["n_samples"] -removed_count ))

    if config["merge_path"] is not None:
        img = merge(config["merge_path"], img)

    if config["output_path"] is not None:
        img.save(config["output_path"] + str(round(time()*1000)) + ".png", format="png")
    else:
        img.show()
    
    if config["plot"]:
        plot.plot(S,E,c)

    return removed_count,pasted, generation_canvas

    # FOR TESTING (UI TEST)
    # E_areas = []
    # for e in E:
    #     E_areas.append(e[2]*e[2]*np.pi)

    
    # return img,config, E_areas


def load_images(path, config, verbose):
    if path[len(path)-1] != '/':
        path += '/'
    files = os.listdir(path)
    imgs = []

    files = list(filter(filter_png, files))
    if len(files) == 0:
        raise BaseException("No files in overlay dir")
    if config["overlay_n"] is None:
        if len(files) == 1:
            config["overlay_n"] = 1
        else:
            config["overlay_n"] = random.randrange(1,len(files))
    n_img = config["overlay_n"]
    if verbose:
        print("Images selected:")
    while n_img > 0:
        i = random.randint(0,len(files)-1)
        if verbose:
            print(files[i] ,end="")
        imgs.append(Image.open(path + files[i]))
        files.remove(files[i])
        n_img -= 1
    if verbose:
        print("\n")
    return imgs


def filter_png(s):
    return s.endswith(".png")


# https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
def resize_pic(img, basewidth):
    wpercent = (basewidth/float(img.size[0]))
    hsize = int(float(img.size[1])*float(wpercent))
    img = img.resize(size=(basewidth,hsize))
    return img


def merge(outer_path, inner):
    outer = Image.open(outer_path)
    if outer.format != 'PNG':
        return inner
    outer_arr = np.array(outer)

    top_left = first_transparent_pixel(outer_arr)
    if top_left is None:
        return inner
    # bottom_right = (top_left[0]+inner.height-1, top_left[1]+inner.width+1)

    # x_c = (top_left[1] + bottom_right[1]) // 2
    # y_c = (top_left[0] + bottom_right[0]) // 2

    outer.paste(inner, (top_left[1],top_left[0]))
    return outer


def trans_paste(fg_img,bg_img,alpha=1.0,box=(0,0)):
    fg_img_trans = Image.new("RGBA",fg_img.size)
    fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
    bg_img.paste(fg_img_trans,box,fg_img_trans)
    return bg_img

# height, width
def first_transparent_pixel(pic_arr):
    for i,P in enumerate(pic_arr):
            for j,p in enumerate(P):
                    if sum(p) == 0:
                        return (i,j)
    return None


# Returns true if small fits entirely on big if pasted at placement
def fits(small, big, placement):
    if (placement[0] + small.width <= big.width) and placement[1] + small.height <= big.height:
        return True
    return False
