# HSI Encode / Viewer

A simple Python script for reading hyperspectral `.HSI` data (BSQ layout), visualizing a selected band, and generating the spectral profile of a single pixel.

The script saves:
- selected band image as PNG,
- pixel spectrum plot as PNG,
- pixel spectrum numeric data as CSV.

---

## Features

- Reads raw `.HSI` data (`uint8`) with header offset support.
- Reshapes raw data into a 3D cube: `(bands, height, width)`.
- Displays a selected band (`band_index`).
- Extracts and plots spectral profile for a selected pixel (`pixel_x_axis`, `pixel_y_axis`).
- Automatically saves outputs to a `plots` folder.

---

## Requirements

- Python 3.9+ (recommended)
- Packages:
  - `numpy`
  - `matplotlib`
  - `pandas`

Install dependencies:

```powershell
pip install numpy matplotlib pandas
