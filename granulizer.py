import argparse
import numpy as np
import soundfile as sf
import os
import sys

def apply_grain_fade(grain: np.ndarray, fade_len: int) -> np.ndarray:
    window = np.ones(len(grain))
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)
    window[:fade_len] = fade_in
    window[-fade_len:] = fade_out

    return grain * window

def main():
    parser = argparse.ArgumentParser(
        description="Granular WAV processor for IR files. "
                    "Splits audio into zero-aligned grains, randomly rearranges them "
                    "with crossfades, and lengthens/shortens the output."
    )
    parser.add_argument("input", help="Path to input WAV file")
    parser.add_argument("output", help="Path to output WAV file")
    parser.add_argument("--grain-size", type=int, required=True,
                        help="Grain size in samples (e.g., 1024, 2048, 4096)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--swap-channels", action="store_true",
                        help="Randomly swap left/right channel assignments per grain")
    parser.add_argument("--overlap-percent", type=float, default=0.66,
                        help="Grain overlap ratio (0.0-1.0). Higher = denser cloud. Default: 0.66")
    parser.add_argument("--length", type=float, default=1.0,
                    help="Output length multiplier relative to input (e.g., 2.0 for 2x length). Default: 1.0")


    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    audio, sr = sf.read(args.input)
    if audio.ndim > 1:
        channels = [audio[:, i] for i in range(audio.shape[1])]
    else:
        channels = [audio]

    fade_len = int(args.grain_size * 0.25)
    fade_len = min(fade_len, args.grain_size // 2)

    grains = []
    for ch in channels:
        num_grains = len(ch) // args.grain_size
        ch_grains = []
        for i in range(num_grains):
            start = i * args.grain_size
            end = start + args.grain_size
            grain = ch[start:end].copy()
            ch_grains.append(apply_grain_fade(grain, fade_len))
        grains.append(ch_grains)


    hop_size = int(args.grain_size * (1.0 - args.overlap_percent))
    hop_size = max(hop_size, fade_len)
    target_len = int(args.length * len(audio))
    num_output_grains = int(np.ceil((target_len - args.grain_size) / hop_size)) + 1


    if args.seed is not None:
        np.random.seed(args.seed)

    num_grains_per_channel = len(grains[0])
    indices = np.random.choice(num_grains_per_channel, size=num_output_grains, replace=True)

    if args.swap_channels and len(channels) == 2:
        swap_flags = np.random.choice([False, True], size=num_output_grains)
    else:
        swap_flags = np.zeros(num_output_grains, dtype=bool)

    out_len = num_output_grains * hop_size + args.grain_size
    output_channels = [np.zeros(out_len) for _ in channels]

    for i, idx in enumerate(indices):
        offset = i * hop_size
        for ch_idx, ch_grains in enumerate(grains):
            target_ch = ch_idx
            if swap_flags[i]:
                target_ch = 1 - ch_idx  # Swap 0 <-> 1

            grain = grains[target_ch][idx]
            end_idx = min(offset + len(grain), len(output_channels[target_ch]))
            start_idx = offset
            output_channels[target_ch][start_idx:end_idx] += grain[start_idx - offset:end_idx - offset]

    if len(channels) > 1:
        output = np.column_stack(output_channels)
    else:
        output = output_channels[0]

    full_len = len(output)
    if output.ndim == 1:
        fade_curve = np.exp(-np.linspace(0, 6.0, full_len))
        output[:] *= fade_curve
    else:
        fade_curve = np.exp(-np.linspace(0, 6.0, full_len)).reshape(-1, 1)
        output[:, :] *= fade_curve


    peak = np.max(np.abs(output))
    if peak > 1.0:
        output /= peak

    sf.write(args.output, output, sr)
    print(f"Processed: {args.input} --> {args.output}")
    print(f"   Input:  {len(audio):,} samples ({len(audio)/sr:.2f}s)")
    print(f"   Output: {len(output):,} samples ({len(output)/sr:.2f}s) "
          f"({len(output)/len(audio)*100:.0f}% of input)")
    print(f"   Grain: {args.grain_size} | Fade: {fade_len} | Hop: {hop_size}")

if __name__ == "__main__":
    main()
