import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

file_path = r"D:\Bazy\Nowe_dane\01.HSI"

filename = os.path.basename(file_path)
base_name = os.path.splitext(filename)[0]
output_dir = os.path.join(os.path.dirname(file_path), "plots")
os.makedirs(output_dir, exist_ok=True)

# Wyliczone parametry
bands = 151
height =750
width = 1000
header_offset = 8

pixel_x_axis = 500
pixel_y_axis = 750
band_index = 100

try:
    # Wczytujemy cały plik prosto do RAMu
    with open(file_path, 'rb') as f:
        f.seek(header_offset)  # Przeskakujemy 8-bajtowy nagłówek

        # Czytamy resztę jako ciąg wartości 8-bitowych
        raw_data = np.fromfile(f, dtype=np.uint8)

        # Nadajemy ciągowi danych odpowiedni kształt 3D (BSQ)
        hsi_cube = raw_data.reshape((bands, height, width))

    # Wyświetlamy pasmo
    plt.figure()
    plt.imshow(hsi_cube[band_index, :, :], cmap='gray')
    plt.title(f"Zdekodowany obraz (pasmo {band_index}) | Plik: {filename}")
    plt.colorbar(label='Intensywność (0-255)')
    plt.tight_layout()

    band_plot_path = os.path.join(output_dir, f"{base_name}_band_{band_index}.png")
    plt.savefig(band_plot_path, dpi=300, bbox_inches='tight')
    plt.show()

    # Wyciągnięcie widma dla przykładowego piksela
    pixel_spectrum = hsi_cube[:, pixel_x_axis, pixel_y_axis]
    pixel_label = f"pixel_X{pixel_x_axis}_Y{pixel_y_axis}"

    # Zapis widma do CSV
    spectrum_csv_path = os.path.join(
        output_dir,
        f"{base_name}_{pixel_x_axis}_{pixel_y_axis}_spectrum.csv"
    )

    spectrum_df = pd.DataFrame({
        "file": filename,
        "pixel_x": [pixel_x_axis] * bands,
        "pixel_y": [pixel_y_axis] * bands,
        "band": np.arange(bands),
        "intensity": pixel_spectrum
    })
    spectrum_df.to_csv(spectrum_csv_path, index=False)

        # Zapis widma także do JSON
    spectrum_json_path = os.path.join(
        output_dir,
        f"{base_name}_{pixel_x_axis}_{pixel_y_axis}_spectrum.json"
    )

    # Przygotowanie struktury JSON: metadane + lista pasm
    spectrum_json = {
        "file": filename,
        "pixel_x": int(pixel_x_axis),
        "pixel_y": int(pixel_y_axis),
        "bands_count": int(bands),
        "bands": [
            {"band": int(b), "intensity": int(v)}
            for b, v in enumerate(pixel_spectrum.tolist())
        ]
    }

    # Zapis do pliku (UTF-8, ładne formatowanie)
    with open(spectrum_json_path, "w", encoding="utf-8") as jf:
        json.dump(spectrum_json, jf, ensure_ascii=False, indent=2)

    # Wykres widma
    plt.figure()
    plt.plot(pixel_spectrum)
    plt.title(
        f"Profil widmowy pojedynczego piksela ({pixel_label}) | Plik: {filename}"
    )
    plt.xlabel("Numer pasma (0-150)")
    plt.ylabel("Intensywność (8-bit)")
    plt.grid(True)
    plt.tight_layout()

    spectrum_plot_path = os.path.join(
        output_dir,
        f"{base_name}_{pixel_x_axis}_{pixel_y_axis}_spectrum.png"
    )
    plt.savefig(spectrum_plot_path, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"Zapisano wykresy do:\n- {band_plot_path}\n- {spectrum_plot_path}")
    print(f"Zapisano CSV do:\n- {spectrum_csv_path}")
    print(f"Zapisano JSON do:\n- {spectrum_json_path}")

except ValueError as e:
    print(f"Błąd kształtu: Prawdopodobnie offset lub wymiary są nieco inne. Szczegóły: {e}")
except Exception as e:
    print(f"Inny błąd podczas dekodowania: {e}")