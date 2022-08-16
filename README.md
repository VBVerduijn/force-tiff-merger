# force-tiff-merger
Merger script to produce images of combined tiff stacks and optical tweezer data.

The following packages need to be installed; all available through pip install xxx:
- matplotlib
- numpy
- gc
- skimage.io
- lumicks.pylake
- multiprocessing
- functools
- tqdm

The prompt can be executed in any shell through 'python main.py'
Following the prompts will yield a force vs time diagram, if other functionality is needed the script needs to be altered.
Specifically for the analysis of both beeds, force2x is requisted first, followed by the force that you want to analysed.
If 'y' of the question to force2x, force2x will be the 2nd line in combination with the chosen option later on.

I.e. If you want a graph with just force2x, choose 'n' for force2x, and choose 'force2x' later in the prompt.
