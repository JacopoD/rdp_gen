import img_gen
import sys
import json

def main():
    verbose = "-v" in sys.argv
    plot = "--plot" in sys.argv
    try:
        i_b = sys.argv.index("-c")
        if len(sys.argv) - 1 >= i_b+1:
            b_path = sys.argv[i_b+1]
        else:
            print("-c was provided with no path, usage: -c [PATH]")
            return
    except ValueError:
        print("No config file provided!")
        return

    with open(b_path) as config_file:
        config = json.load(config_file)
        
        if plot:
            config["plot"] = True
        else:
            config["plot"] = False
        
        if verbose:
            config["verbose"] = True
        else:
            config["verbose"] = False
        parse_config(config)

    img_gen.generate_img(config)

OPTIONAL = ["background_path", "output_path", "merge_path", "ellipse_ranges", "ellipse_ratios","wse_background", "ellipses_wse", "overlay_n", "overlays_scaling"]

def parse_config(config):
    if (not "n_samples" in config) or (not "n_clusters" in config) or (not "overlays_path" in config):
        raise ValueError("n_samples, n_clusters and overlays_path must be provided in config file")
    
    for c in OPTIONAL:
        if c not in config:
            config[c] = None
            

if __name__ == "__main__":
    main()