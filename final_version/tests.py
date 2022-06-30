import time
from img_gen import generate_img


def execution_time():
    config = {
        "background_path": None,
        "output_path": None,
        "overlays_path": "./insects/",
        "merge_path": None,

        "n_samples": 300,
        "overlay_n":None,
        "n_clusters": 2,
        "ellipse_ranges": None,
        "ellipse_ratios": None,
        "wse_background": None,
        "ellipses_wse": None,
        "plot": False,
        "verbose": False
    }

    print("input,removed_wse,removed_fit,output")

    for i in range(100,10100,100):
        config["n_samples"] = i
        # start_time = time.time()
        removed_count,pasted = generate_img(config)
        print("{},{},{},{}".format(i, removed_count, i - removed_count - (removed_count - pasted), pasted))
        # print("{},{}".format(i, time.time()- start_time))


if __name__ == "__main__":
    execution_time()

