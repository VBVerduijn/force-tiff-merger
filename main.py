import matplotlib.pyplot as plt
import numpy as np
import gc
import skimage.io as skio
import lumicks.pylake as lk
from multiprocessing import Pool
from functools import partial
import tqdm


def init():
    print("\n")
    print("\n")
    print("\n")
    print("\033[1;32m *********************************************************")
    print("Made by V.B. Verduijn; v.b.verduijn@rug.nl")
    print("Version 1.3")
    print("Do not reproduce without permission")
    print("Github: https://github.com/VBVerduijn/force-tiff-merger")
    print("*********************************************************")
    print("\033[1;37m \n")
    print("\n")
    print("\n")

    print("All plugins have been initialised")


def checker(data_):  # Prompting function to obtain the dataset to be used, as well as the marker and the down-sampling
    # number.
    print(data_)
    chosen_ = input("Which force curve needs to be selected? FORMAT = 'forceNx': ")
    stop = False
    while not stop:
        if hasattr(data_, chosen_):
            stop = True
        else:
            chosen_ = input("INCORRECT NAME; Which force curve needs to be selected? FORMAT = 'forceNx': ")
    chosen_marker_ = input("What is the marker name? ")
    downsampling_ = input("What is the down-sampling? ")
    print("Data is being down-sampled, this may take some time!")
    return chosen_, chosen_marker_, downsampling_


def pre_proc(data_, two=False):
    # Large plots
    if two:
        # Importing the datastream
        fn = f"{data_}"  # Dictating the file name
        data = lk.File(fn)  # Read in data

        chosen_, chosen_marker_, downsampling_ = checker(
            data)  # give back the chosen dataset and the chosen marker for the tiff-stack

        time_ = getattr(data, chosen_).downsampled_by(
            int(downsampling_)).timestamps / 1e9  # Calculate the time in seconds (since Epoch (Jan 1st 1990)).
        time_ = time_ - time_[0]  # Making the time relative time since start of measurement; time[0] being the start.
        marker = data.markers[chosen_marker_]  # Obtaining the marker
        start_vid = marker.start / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[
            0]  # Calculating the start time of the video
        end_vid = marker.stop / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[
            0]  # Calculating the end time of the video
        markers_ = [start_vid, end_vid]  # Making a parser list for the start and end
        return getattr(data, chosen_).downsampled_by(int(downsampling_)), getattr(data, "force2x").downsampled_by(
            int(downsampling_)), time_, markers_  # Returning the downsampled data and the markers for the graph

    if not two:  # Same function as above but now the additional force2x is ignored.
        # Importing the datastream
        fn = f"{data_}"
        data = lk.File(fn)  # read in data
        chosen_, chosen_marker_, downsampling_ = checker(data)

        time_ = getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9
        time_ = time_ - time_[0]
        marker = data.markers[chosen_marker_]
        start_vid = marker.start / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[0]
        end_vid = marker.stop / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[0]
        markers_ = [start_vid, end_vid]
        return getattr(data, chosen_).downsampled_by(int(downsampling_)), time_, markers_

    else:
        print("An error has occurred, fill in data file as string ending in .h5")


def extract_vid():
    video_ = input("What is the tiff-stack location? [FULL PATH] ")
    imstack_ = skio.imread(video_, plugin="tifffile")
    length_ = int(imstack.shape[0])
    dimensions_ = [imstack.shape[1], imstack.shape[2]]
    return imstack_, length_, dimensions_


def process(dataset_, time_, imstack_, length_, markers_, dataset2_=False):
    time_step_ = np.float64((markers_[1] - markers_[0]) / length_)
    dpi_setting_ = input("What is the DPI setting? ")
    frame_rate_ = input("What is the video frame-rate? ")
    output_dir_ = input("What is the required output directory? [MUST EXIST!; FULL PATH] ")
    print(f"The frames are being outputted to: {output_dir_}, this may take some time!")
    return [time_step_, dpi_setting_, frame_rate_, output_dir_, length_, markers_], dataset_, time_, imstack_, dataset2_


def create(in_, ims_, t_, ds_, ds2_, x):
    fig, ax = plt.subplots(1, 2, figsize=(24, 4), dpi=int(in_[1]))

    ax[0].imshow(ims_[x], cmap="gray")
    ax[0].axis(False)
    ax[0].set_title("Microscopy Image")

    ax[1].set_title("Time - Force Data (1x)")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Force (pN)")
    ax[1].grid()
    ax[1].plot(t_, ds_.data, label="force1x")

    if ds2_:
        ax[1].plot(t_, ds2_.data, c="black", label="force2x")
    ax[1].set_xlim(left=0)
    ax[1].axvline(in_[0] * x + in_[-1][0], c="red")

    plt.legend()

    fig.tight_layout()
    fig.savefig(f"{in_[3]}/{x}.png", bbox_inches='tight', pad_inches=0.1)
    plt.cla()
    plt.clf()
    plt.close('all')
    plt.close(fig)
    gc.collect()

    return True


if __name__ == '__main__':
    init()

    data_file = input("What is the data-file name? [FULL PATH] ")
    multiple_forces = input("Do you want force2x as a second line in the graph? [y/n] ")

    if multiple_forces == "y":
        chosen_data, chosen_data2, time, markers = pre_proc(data_file, True)
        imstack, length, dimensions = extract_vid()
        inp, ds, t, ims, ds2 = process(chosen_data, time, imstack, length, markers, chosen_data2)
    else:
        print("Output was different then 'y'; therefore, defaulting to 'n'.")
        chosen_data, time, markers = pre_proc(data_file, False)
        imstack, length, dimensions = extract_vid()
        inp, ds, t, ims, ds2 = process(chosen_data, time, imstack, length, markers)

    pool = Pool()
    try:
        pool.map(partial(create, inp, ims, t, ds, ds2),
                 tqdm.tqdm(np.arange(0, int(inp[4]), step=int(inp[2]))))

    finally:  # To make sure processes are closed in the end, even if errors happen
        print("Output has been completed!")
        pool.close()
        pool.join()
