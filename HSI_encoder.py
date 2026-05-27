import argparse
import os

import matplotlib.pyplot as plt

from config import (
    band_index as cfg_band_index,
    bands as cfg_bands,
    file_path as cfg_file_path,
    header_offset as cfg_header_offset,
    height as cfg_height,
    pixel_x_axis as cfg_pixel_x_axis,
    pixel_y_axis as cfg_pixel_y_axis,
    width as cfg_width,
)
from hsi_export import export_band_json, export_spectrum_files
from hsi_io import load_hsi_cube, prepare_output_dir, validate_indices
from hsi_plot import create_band_figure, create_spectrum_figure


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read BSQ .HSI file, visualize a band and export pixel spectrum."
    )
    parser.add_argument("--file-path", default=cfg_file_path, help="Path to .HSI file")
    parser.add_argument("--bands", type=int, default=cfg_bands, help="Number of bands")
    parser.add_argument("--height", type=int, default=cfg_height, help="Image height")
    parser.add_argument("--width", type=int, default=cfg_width, help="Image width")
    parser.add_argument(
        "--header-offset",
        type=int,
        default=cfg_header_offset,
        help="Header offset in bytes",
    )
    parser.add_argument(
        "--band-index",
        type=int,
        default=cfg_band_index,
        help="Band index to visualize/export",
    )
    parser.add_argument(
        "--pixel-x",
        type=int,
        default=cfg_pixel_x_axis,
        help="Pixel X coordinate",
    )
    parser.add_argument(
        "--pixel-y",
        type=int,
        default=cfg_pixel_y_axis,
        help="Pixel Y coordinate",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Do not show matplotlib windows",
    )
    return parser.parse_args()


def run_pipeline(
    file_path,
    bands,
    height,
    width,
    header_offset,
    band_index,
    pixel_x_axis,
    pixel_y_axis,
    no_display=False,
):
    filename, base_name, output_dir = prepare_output_dir(file_path)

    validate_indices(
        band_index=band_index,
        pixel_x=pixel_x_axis,
        pixel_y=pixel_y_axis,
        bands=bands,
        width=width,
        height=height,
    )

    hsi_cube = load_hsi_cube(file_path, bands, height, width, header_offset)

    band_image, band_json_path = export_band_json(
        hsi_cube, band_index, filename, base_name, output_dir
    )
    band_fig = create_band_figure(band_image, band_index, filename)
    band_plot_path = os.path.join(output_dir, f"{base_name}_band_{band_index}.png")
    band_fig.savefig(band_plot_path, dpi=300, bbox_inches="tight")

    pixel_spectrum = hsi_cube[:, pixel_y_axis, pixel_x_axis]
    pixel_label = f"pixel_X{pixel_x_axis}_Y{pixel_y_axis}"

    spectrum_csv_path, spectrum_json_path = export_spectrum_files(
        pixel_spectrum,
        bands,
        pixel_x_axis,
        pixel_y_axis,
        filename,
        base_name,
        output_dir,
    )
    spectrum_fig = create_spectrum_figure(pixel_spectrum, pixel_label, filename, bands)
    spectrum_plot_path = os.path.join(
        output_dir, f"{base_name}_{pixel_x_axis}_{pixel_y_axis}_spectrum.png"
    )
    spectrum_fig.savefig(spectrum_plot_path, dpi=300, bbox_inches="tight")

    if no_display:
        plt.close("all")
    else:
        plt.show()

    print(f"Zapisano wykresy do:\n- {band_plot_path}\n- {spectrum_plot_path}")
    print(f"Zapisano CSV do:\n- {spectrum_csv_path}")
    print(f"Zapisano JSON do:\n- {spectrum_json_path}")
    print(f"Zapisano JSON pasma do:\n- {band_json_path}")


def main():
    args = parse_args()
    run_pipeline(
        file_path=args.file_path,
        bands=args.bands,
        height=args.height,
        width=args.width,
        header_offset=args.header_offset,
        band_index=args.band_index,
        pixel_x_axis=args.pixel_x,
        pixel_y_axis=args.pixel_y,
        no_display=args.no_display,
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Błąd: {e}")
    except Exception as e:
        print(f"Inny błąd podczas dekodowania: {e}")