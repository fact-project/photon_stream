import numpy as np


def inspect_run(run):
    analog_amplitude_saturations = []
    total_photon_counts = []
    trigger_types = []
    times = []
    zenith_distances = []
    azimuths = []
    ids = []

    for event in run:
        pixel_intensities = event.photon_stream.photon_count
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
        'ids': np.array(ids),
    }



def add2ax_photon_count_vs_saturations(ax, total_photon_counts, analog_amplitude_saturations):
    ax.plot(total_photon_counts, analog_amplitude_saturations)