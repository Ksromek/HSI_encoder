# HSI Encode / Viewer

A simple Python script for reading hyperspectral `.HSI` data (BSQ layout), visualizing a selected band, and generating the spectral profile of a single pixel.

The script saves:
- selected band image as PNG,
- band matrix as readable JSON,
- pixel spectrum plot as PNG,
- pixel spectrum numeric data as CSV,
- pixel spectrum data as JSON.

---

## Features

- Reads raw `.HSI` data (`uint8`) with header offset support.
- Reshapes raw data into a 3D cube: `(bands, height, width)`.
- Displays a selected band (`band_index`).
- Extracts and plots spectral profile for a selected pixel (`pixel_x_axis`, `pixel_y_axis`).
- Automatically saves outputs to a `plots` folder next to the input file.

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
```

---

## Configuration (edit `HSI_encoder.py`)

- `file_path` — path to the HSI file (BSQ, 8-bit).
- `bands`, `height`, `width`, `header_offset` — file parameters (adjust to match your HSI file).
- `band_index` — which band to visualize/export (0-based).
- `pixel_x_axis`, `pixel_y_axis` — coordinates (x, y) of the pixel whose spectrum is exported.

---

## Output files

Default folder: `plots` next to the input file.

- `{base_name}_band_{band_index}.png` — band image (PNG)
- `{base_name}_band_{band_index}.json` — band matrix saved as readable JSON (rows format)
- `{base_name}_{pixel_x}_{pixel_y}_spectrum.csv` — pixel spectrum (CSV) ready for spreadsheets
- `{base_name}_{pixel_x}_{pixel_y}_spectrum.json` — pixel spectrum (JSON)
- `{base_name}_{pixel_x}_{pixel_y}_spectrum.png` — pixel spectrum plot (PNG)

---

## Data formats

### Band JSON format (rows — readable, 0-based)
```json
{
  "file": "<filename>",
  "band_index": "<int>",
  "width": "<int>",
  "height": "<int>",
  "indexing": "0-based",
  "rows": [
    {"y": 0, "pixels": ["<int>", "<int>", "<int>", "..."]},
    {"y": 1, "pixels": ["<int>", "<int>", "<int>", "..."]}
  ]
}
```

### Pixel spectrum JSON example
```json
{
  "file": "<filename>",
  "pixel_x": "<int>",
  "pixel_y": "<int>",
  "bands_count": "<int>",
  "bands": [
    {"band": 0, "intensity": "<int>"},
    {"band": 1, "intensity": "<int>"},
    "..."
  ]
}
```
