import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np

from hsi_export import export_band_json, export_spectrum_files
from hsi_io import prepare_output_dir, validate_indices
from hsi_plot import create_band_figure, create_spectrum_figure


class TestHSIEncoderPipeline(unittest.TestCase):
    def test_validate_indices_should_accept_valid_values(self):
        validate_indices(
            band_index=1,
            pixel_x=2,
            pixel_y=3,
            bands=5,
            width=10,
            height=10,
        )

    def test_validate_indices_should_raise_when_band_index_is_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_indices(
                band_index=5,
                pixel_x=2,
                pixel_y=3,
                bands=5,
                width=10,
                height=10,
            )

    def test_validate_indices_should_raise_when_pixel_x_is_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_indices(
                band_index=1,
                pixel_x=10,
                pixel_y=3,
                bands=5,
                width=10,
                height=10,
            )

    def test_validate_indices_should_raise_when_pixel_y_is_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_indices(
                band_index=1,
                pixel_x=2,
                pixel_y=10,
                bands=5,
                width=10,
                height=10,
            )

    def test_prepare_output_dir_should_create_plots_folder_next_to_input_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_file = os.path.join(tmpdir, "sample.HSI")
            with open(fake_file, "wb") as f:
                f.write(b"dummy")

            filename, base_name, output_dir = prepare_output_dir(fake_file)

            self.assertEqual(filename, "sample.HSI")
            self.assertEqual(base_name, "sample")
            self.assertTrue(os.path.isdir(output_dir))
            self.assertTrue(output_dir.endswith("plots"))

    def test_export_band_json_should_create_json_file_and_return_band_image(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            hsi_cube = np.arange(2 * 3 * 4, dtype=np.uint8).reshape((2, 3, 4))

            band_image, band_json_path = export_band_json(
                hsi_cube=hsi_cube,
                band_index=1,
                filename="sample.HSI",
                base_name="sample",
                output_dir=tmpdir,
            )

            self.assertTrue(os.path.isfile(band_json_path))
            self.assertEqual(band_image.shape, (3, 4))

    def test_export_spectrum_files_should_create_csv_and_json_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pixel_spectrum = np.array([10, 20], dtype=np.uint8)

            spectrum_csv_path, spectrum_json_path = export_spectrum_files(
                pixel_spectrum=pixel_spectrum,
                bands=2,
                pixel_x=2,
                pixel_y=1,
                filename="sample.HSI",
                base_name="sample",
                output_dir=tmpdir,
            )

            self.assertTrue(os.path.isfile(spectrum_csv_path))
            self.assertTrue(os.path.isfile(spectrum_json_path))

    def test_create_band_figure_should_return_matplotlib_figure(self):
        band_image = np.arange(12).reshape((3, 4))
        fig = create_band_figure(band_image, 1, "sample.HSI")
        self.assertIsNotNone(fig)

    def test_create_spectrum_figure_should_return_matplotlib_figure(self):
        pixel_spectrum = np.array([1, 2, 3])
        fig = create_spectrum_figure(pixel_spectrum, "pixel_X2_Y1", "sample.HSI", 3)
        self.assertIsNotNone(fig)


if __name__ == "__main__":
    unittest.main()