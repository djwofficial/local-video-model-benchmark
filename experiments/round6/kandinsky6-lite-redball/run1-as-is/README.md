# Run 1 (as is, stopped)

Pipeline defaults with VAE tiling: after the first VAE decode the PyTorch MPS allocator kept ~27 GiB cached (tensors only ~6.5-8 GiB), so the process stayed at ~28.8 GiB phys_footprint and swapped heavily. Warm-up seed 41: 520 s; seed 42: 928 s. Stopped by Claude during seed 43 and rerun with cache release between denoising and decoding (run 2 in the parent folder).
