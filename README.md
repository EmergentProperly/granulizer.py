## Install the requirements:

`pip install numpy soundfile`

## Example:

`python3 granulizer.py input.wav output.wav --grain-size 512 --swap-channels --overlap-percent 0.9 --length 3.0`

--grain-size determines the number of samples per grain. Smaller = smoother/noisier; larger = chunkier (more of the original form is preserved per grain).

--swap-channel randomly swaps the grain stereo channels

--overlap-percent determines the amount at which grains overlap each other

--length determines the length of the final output (as a multiplication). So --length 3.0 would be 300% longer than the source file.
