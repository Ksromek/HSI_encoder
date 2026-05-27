import os
import numpy as np


def prepare_output_dir(file_path):
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0]
    output_dir = os.path.join(os.path.dirname(file_path), "plots")
    os.makedirs(output_dir, exist_ok=True)
    return filename, base_name, output_dir


def validate_indices(band_index, pixel_x, pixel_y, bands, width, height):
    if not (0 <= band_index < bands):
        raise ValueError(f"band_index poza zakresem: 0..{bands - 1}")
    if not (0 <= pixel_x < width):
        raise ValueError(f"pixel_x poza zakresem: 0..{width - 1}")
    if not (0 <= pixel_y < height):
        raise ValueError(f"pixel_y poza zakresem: 0..{height - 1}")


def load_hsi_cube(file_path, bands, height, width, header_offset):
    with open(file_path, "rb") as f:
        f.seek(header_offset)
        raw_data = np.fromfile(f, dtype=np.uint8)

    expected_size = bands * height * width
    if raw_data.size != expected_size:
        raise ValueError(
            f"Nie zgadza się rozmiar danych: got {raw_data.size}, expected {expected_size}. "
            "Sprawdź bands/height/width/header_offset."
        )

    return raw_data.reshape((bands, height, width))