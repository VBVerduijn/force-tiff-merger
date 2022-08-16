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
    print("*********************************************************")
    print("Made by V.B. Verduijn; v.b.verduijn@rug.nl")
    print("Version 1.3")
    print("Do not reproduce without persmission")
    print("Github: ")
    print("*********************************************************")
    print("\n")
    print("\n")
    print("\n")

    print("All plugins have been initialised")


def checker(data_):
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
    print("Data is being downsampled, this may take some time!")
    return chosen_, chosen_marker_, downsampling_


def pre_proc(data_, two=False):
    # Large plots
    if two:
        # Importing the datastream
        fn = f"{data_}"
        data = lk.File(fn)  # read in data
        # Add selection menu for this
        chosen_, chosen_marker_, downsampling_ = checker(data)

        time = getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9
        time = time - time[0]
        marker = data.markers[chosen_marker_]
        start_vid = marker.start / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[0]
        end_vid = marker.stop / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[0]
        markers = [start_vid, end_vid]
        return getattr(data, chosen_).downsampled_by(int(downsampling_)), getattr(data, "force2x").downsampled_by(
            int(downsampling_)), time, markers
    if not two:
        # Importing the datastream
        fn = f"{data_}"
        data = lk.File(fn)  # read in data
        # Add selection menu for this
        chosen_, chosen_marker_, downsampling_ = checker(data)

        time = getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9
        time = time - time[0]
        marker = data.markers[chosen_marker_]
        start_vid = marker.start / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[0]
        end_vid = marker.stop / 1e9 - (getattr(data, chosen_).downsampled_by(int(downsampling_)).timestamps / 1e9)[0]
        markers = [start_vid, end_vid]
        return getattr(data, chosen_).downsampled_by(int(downsampling_)), time, markers

    else:
        print("An error has occured, fill in data file as string ending in .h5")


def extract_vid():
    video = input("What is the tiff-stack location? [FULL PATH] ")
    imstack = skio.imread(video, plugin="tifffile")
    length_ = int(imstack.shape[0])
    dimensions_ = [imstack.shape[1], imstack.shape[2]]
    return imstack, length_, dimensions_


def process(dataset_, time_, imstack_, length_, markers_, dataset2_=False):
    time_step = np.float64((markers_[1] - markers_[0]) / length_)
    dpi_setting = input("What is the DPI setting? ")
    frame_rate = input("What is the video frame-rate? ")
    output_dir = input("What is the required output directory? [MUST EXIST!; FULL PATH] ")
    print(f"The frames are being outputted to: {output_dir}, this may take some time!")
    return [time_step, dpi_setting, frame_rate, output_dir, length_, markers_], dataset_, time_, imstack_, dataset2_


def create(inputs_, imstack_, time_, dataset_, dataset2_, x):
    fig, ax = plt.subplots(1, 2, figsize=(24, 4), dpi=int(inputs_[1]))

    ax[0].imshow(imstack_[x], cmap="gray")
    ax[0].axis(False)
    ax[0].set_title("Microscopy Image")

    ax[1].set_title("Time - Force Data (1x)")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Force (pN)")
    ax[1].grid()
    ax[1].plot(time_, dataset_.data, label="force1x")

    if dataset2_:
        ax[1].plot(time_, dataset2_.data, c="black", label="force2x")
    ax[1].set_xlim(left=0)
    ax[1].axvline(inputs_[0] * x + inputs_[-1][0], c="red")

    plt.legend()

    fig.tight_layout()
    fig.savefig(f"{inputs_[3]}/{x}.png", bbox_inches='tight', pad_inches=0.1)
    plt.cla()
    plt.clf()
    plt.close('all')
    plt.close(fig)
    gc.collect()

    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    init()

    data_file = input("What is the data-file name? [FULL PATH] ")
    multiple_forces = input("Do you want force2x as a second line in the graph? [y/n] ")

    if multiple_forces == "y":
        # if input==False:
        #    data_file = "C:/LP040722-Ctrap/20220704-152046 Marker 1.h5"
        chosen_data, chosen_data2, time, markers = pre_proc(data_file, True)
        imstack, length, dimensions = extract_vid()
        inputs_, dataset_, time_, imstack_, dataset2_ = process(chosen_data, time, imstack, length, markers,
                                                                chosen_data2)
    else:
        print("Output was different then 'y'; therefore, defaulting to 'n'.")
        chosen_data, time, markers = pre_proc(data_file, False)
        imstack, length, dimensions = extract_vid()
        inputs_, dataset_, time_, imstack_, dataset2_ = process(chosen_data, time, imstack, length, markers)

    pool = Pool()
    try:
        pool.map(partial(create, inputs_, imstack_, time_, dataset_, dataset2_),
                 tqdm.tqdm(np.arange(0, int(inputs_[4]), step=int(inputs_[2]))))

    finally:  # To make sure processes are closed in the end, even if errors happen
        print("Output has been completed!")
        pool.close()
        pool.join()
