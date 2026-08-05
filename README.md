## Install the requirements:

`pip install numpy soundfile`

## Example:

`python3 granulizer.py input.wav output.wav --grain-size 512 --swap-channels --overlap-percent 0.9`

--grain-size - the number of samples per grain. Smaller = smoother/noisier; larger = chunkier (more of the original form is preserved per grain).

--swap-channel - randomly swaps the grain stereo channels

--overlap-percent - the amount at which grains overlap each other

Note: the script applies an exponential fade to the output
