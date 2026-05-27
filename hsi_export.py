import json
import os

import numpy as np
import pandas as pd


def export_band_json(hsi_cube, band_index, filename, base_name, output_dir):
    band_image = hsi_cube[band_index, :, :].astype(int)
    band_json_path = os.path.join(output_dir, f"{base_name}_band_{band_index}.json")

    band_h, band_w = band_image.shape
    rows = [{"y": int(y), "pixels": band_image[y, :].tolist()} for y in range(band_h)]

    band_payload = {
        "file": filename,
        "band_index": int(band_index),
        "width": int(band_w),
        "height": int(band_h),
        "indexing": "0-based",
        "rows": rows,
    }

    with open(band_json_path, "w", encoding="utf-8") as bf:
        json.dump(band_payload, bf, ensure_ascii=False, indent=2)

    return band_image, band_json_path


def export_spectrum_files(pixel_spectrum, bands, pixel_x, pixel_y, filename, base_name, output_dir):
    spectrum_csv_path = os.path.join(output_dir, f"{base_name}_{pixel_x}_{pixel_y}_spectrum.csv")
    spectrum_json_path = os.path.join(output_dir, f"{base_name}_{pixel_x}_{pixel_y}_spectrum.json")

    spectrum_df = pd.DataFrame({
        "file": filename,
        "pixel_x": [pixel_x] * bands,
        "pixel_y": [pixel_y] * bands,
        "band": np.arange(bands),
        "intensity": pixel_spectrum,
    })
    spectrum_df.to_csv(spectrum_csv_path, index=False)

    spectrum_json = {
        "file": filename,
        "pixel_x": int(pixel_x),
        "pixel_y": int(pixel_y),
        "bands_count": int(bands),
        "bands": [
            {"band": int(b), "intensity": int(v)}
            for b, v in enumerate(pixel_spectrum.tolist())
        ],
    }

    with open(spectrum_json_path, "w", encoding="utf-8") as jf:
        json.dump(spectrum_json, jf, ensure_ascii=False, indent=2)

    return spectrum_csv_path, spectrum_json_path