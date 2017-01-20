import pandas as pd


def add2ax_photon_count_vs_saturations(
        axis,
        total_photon_counts,
        analog_amplitude_saturations):
    axis.plot(total_photon_counts, analog_amplitude_saturations)
