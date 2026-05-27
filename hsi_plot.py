import matplotlib.pyplot as plt


def create_band_figure(band_image, band_index, filename):
    fig, ax = plt.subplots()
    im = ax.imshow(band_image, cmap="gray")
    ax.set_title(f"Zdekodowany obraz (pasmo {band_index}) | Plik: {filename}")
    fig.colorbar(im, ax=ax, label="Intensywność (0-255)")
    fig.tight_layout()
    return fig


def create_spectrum_figure(pixel_spectrum, pixel_label, filename, bands):
    fig, ax = plt.subplots()
    ax.plot(pixel_spectrum)
    ax.set_title(f"Profil widmowy pojedynczego piksela ({pixel_label}) | Plik: {filename}")
    ax.set_xlabel(f"Numer pasma (0-{bands - 1})")
    ax.set_ylabel("Intensywność (8-bit)")
    ax.grid(True)
    fig.tight_layout()
    return fig