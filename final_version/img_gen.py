import os
import sys
from PIL import Image
import random
from canvas import generate_canvas
from time import time
import numpy as np
import plot


PLOT = False

def main():
    global PLOT

    verbose = "-v" in sys.argv
    b_path = None
    o_path = None
    merge_path = None
    try:
        i_b = sys.argv.index("-b")
        if len(sys.argv) - 1 >= i_b+1:
            b_path = sys.argv[i_b+1]
        else:
            print("-b was provided with no path, usage: -b [PATH]")
            return
    except ValueError:
        print("No background provided, default will be used")
        pass

    try:
        i_o = sys.argv.index("-o")
        if len(sys.argv) - 1 >= i_o+1:
            o_path = sys.argv[i_o+1]
            if o_path[len(o_path)-1] != "/":
                o_path += "/"
        else:
            print("-o was provided with no path, usage: -o [PATH]")
            return
    except ValueError:
        print("No output path provided")
        pass

    try:
        i_merge = sys.argv.index("-m")
        if len(sys.argv) - 1 >= i_merge+1:
            merge_path = sys.argv[i_merge+1]
        else:
            print("-m was provided with no path, usage: -m [PATH]")
            return
    except ValueError:
        print("No merging")
        pass

    try:
        sys.argv.index("--plot")
        PLOT = True
    except ValueError:
        pass

    generate_img("./insects/", 4, background_path=b_path, output_path=o_path, verbose=verbose, merge_path=merge_path)

# def generate_img(overlays_path, overlay_n, background_path = None, verbose = False, output_path = None, merge_path = None):
# canvas = (1000,1000)
#     if background_path == None:
#         img = Image.new("RGB", (canvas[0], canvas[1]), "white")
#     else:
#         img = Image.open(background_path)
#         canvas = img.size
#     if verbose:
#         print("Background image size: {}".format(canvas))

#     overlay_scaling = 0.05

#     overlays = load_images(overlays_path, overlay_n, verbose)

#     for i in range(len(overlays)):
#         overlays[i] = resize_pic(overlays[i], round(canvas[0] * overlay_scaling))

#     generation_canvas_scaling = 0.03

#     generation_canvas = (round(canvas[0]* generation_canvas_scaling),round(canvas[1]* generation_canvas_scaling))

#     if verbose:
#         print("Generation canvas size: {}".format(generation_canvas))

#     # S, E, c = generate_canvas(
#     #     width=generation_canvas[0], height=generation_canvas[1], n_samples=400, n_ellipses=5,
#     #     ellipse_ranges=[(5, 10), (2, 7), (2, 3), (4, 7), (2, 5)],
#     #     ellipse_ratios=[(0.6, 0.8), (0.9, 1), (0.3, 0.8),(0.3, 0.8),(0.3, 0.8)],
#     #     wse_factor_background=0.8,
#     #     ellipse_wse=[0.6, 0.7, 0.4, 0.5, 0.8],
#     #     verbose=verbose
#     # )

#     n_samples = 600



#     S, E, c, removed_count = generate_canvas(
#         width=generation_canvas[0], height=generation_canvas[1], n_samples=n_samples, n_ellipses=2,
#         ellipse_ranges=[(20, 25), (15, 20)],
#         ellipse_ratios=[(0.6, 0.8), (0.2, 0.3)],
#         wse_factor_background=1,
#         ellipse_wse=[0.8,0.6],
#         verbose=verbose
#     )

#     pasted = 0
    
#     for s in S:
#         if s[2] == -2:
#             continue
#         p_scaled = [round(s[0] * canvas[0] / generation_canvas[0]), round(s[1] * canvas[1] / generation_canvas[1])]
#         # print("{},{} --> {},{}".format(s[0],s[1],p_scaled[0],p_scaled[1]))
#         i = random.randint(0, overlay_n-1)
#         ov = overlays[i].rotate(random.randint(0,360), resample=Image.Resampling.BICUBIC)
        
#         if fits(ov, img, p_scaled):
#             pasted += 1
#             img.paste(ov, p_scaled, ov)

#     if verbose:
#         print("{}/{} samples fit on the final image".format(pasted, n_samples -removed_count ))

#     if merge_path is not None:
#         img = merge(merge_path, img)

#     if output_path is not None:
#         img.save(output_path + str(round(time()*1000)) + ".png", format="png")
#     else:
#         img.show()
    
#     if PLOT:
#         plot.plot(S,E,c)

def generate_img(config):
    canvas = (1000,1000)
    if config["background_path"] == None:
        img = Image.new("RGB", (canvas[0], canvas[1]), "white")
    else:
        img = Image.open(config["background_path"])
        canvas = img.size
    if config["verbose"]:
        print("Background image size: {}".format(canvas))

    overlay_scaling = 0.05

    overlays = load_images(config["overlays_path"], config, config["verbose"])

    for i in range(len(overlays)):
        overlays[i] = resize_pic(overlays[i], round(canvas[0] * overlay_scaling))

    generation_canvas_scaling = 0.03

    generation_canvas = (round(canvas[0]* generation_canvas_scaling),round(canvas[1]* generation_canvas_scaling))

    if config["verbose"]:
        print("Generation canvas size: {}".format(generation_canvas))


    rng = np.random.default_rng()


    if config["ellipses_wse"] is None:
        config["ellipses_wse"] = rng.uniform(0.8,1,config["n_clusters"])

    if config["wse_background"] is None:
        config["wse_background"] = rng.uniform(0,1)

    if config["ellipse_ranges"] is None:
        config["ellipse_ranges"] = [rng.uniform(min(generation_canvas)/2, max(generation_canvas)/2, 2)]  * config["n_clusters"]

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
        ov = overlays[i].rotate(random.randint(0,360), resample=Image.Resampling.BICUBIC)
        
        if fits(ov, img, p_scaled):
            pasted += 1
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


def load_images(path, config, verbose):
    if path[len(path)-1] != '/':
        path += '/'
    files = os.listdir(path)
    imgs = []

    files = list(filter(filter_png, files))
    if len(files) == 0:
        raise BaseException("No files in overlay dir")
    if config["overlay_n"] is None:
        config["overlay_n"] = random.randint(1,len(files)-1)
    n_img = config["overlay_n"]
    if verbose:
        print("Images selected:")
    while n_img > 0:
        i = random.randint(0,len(files)-1)
        if verbose:
            print(files[i] ,end="")
        imgs.append(Image.open(path + files[i]))
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
    outer_arr = np.array(outer)

    top_left = first_transparent_pixel(outer_arr)
    # bottom_right = (top_left[0]+inner.height-1, top_left[1]+inner.width+1)

    # x_c = (top_left[1] + bottom_right[1]) // 2
    # y_c = (top_left[0] + bottom_right[0]) // 2

    outer.paste(inner, (top_left[1],top_left[0]))
    return outer


# height, width
def first_transparent_pixel(pic_arr):
     for i,P in enumerate(pic_arr):
             for j,p in enumerate(P):
                     if sum(p) == 0:
                             return (i,j)


# Returns true if small fits entirely on big if pasted at placement
def fits(small, big, placement):
    if (placement[0] + small.width <= big.width) and placement[1] + small.height <= big.height:
        return True
    return False

if __name__ == "__main__":
    main()