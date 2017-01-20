import numpy as np
import matplotlib.pyplot as plt


def inspect_run(run):
    analog_amplitude_saturations = []
    total_photon_counts = []
    trigger_types = []
    times = []
    zenith_distances = []
    azimuths = []
    ids = []

    for event in run:
        pixel_intensities = photon_integral_over_time(event)
        analog_amplitude_saturations.append(len(event.amplitude_saturated_pixels))
        total_photon_counts.append(pixel_intensities.sum())
        trigger_types.append(event.trigger_type)
        times.append(float(event._time_unix_s)+float(event._time_unix_us)*1e-6)
        zenith_distances.append(event.zd)
        azimuths.append(event.az)
        ids.append(event.id)

    return {
        'analog_amplitude_saturations': np.array(analog_amplitude_saturations),
        'trigger_types': np.array(trigger_types),
        'total_photon_counts': np.array(total_photon_counts),
        'times': np.array(times),
        'zenith_distances': np.array(zenith_distances),
        'azimuths': np.array(azimuths),
        'ids': np.array(ids),}


def photon_integral_over_time(event):
    pixel_intensities = np.zeros(len(event.photon_stream.time_lines))
    for pixel, time_line in enumerate(event.photon_stream.time_lines):
        pixel_intensities[pixel] = len(time_line)
    return pixel_intensities


def add2ax_photon_count_vs_saturations(ax, total_photon_counts, analog_amplitude_saturations):
    ax.plot(total_photon_counts, analog_amplitude_saturations)