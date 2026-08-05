## Install the requirements:

`pip install numpy soundfile`

## Example:

`python3 granulizer.py input.wav output.wav --grain-size 512 --swap-channels --overlap-percent 0.9`

--grain-size determines the number of samples per grain. Smaller = smoother/noisier; larger = chunkier (more of the original form is preserved per grain).

--swap-channel randomly swaps the grain stereo channels

--overlap-percent determines the amount at which grains overlap each other


For a longer/shorter output, adjust:

`target_len = 1 * len(audio)`

(>1 lengthens; <1 shortens). e.g:

`target_len = 2 * len(audio)`

^^^ the output will be twice the length of the input.
