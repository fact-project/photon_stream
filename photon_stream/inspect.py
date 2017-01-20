import pandas as pd

def inspect_run(run):
    return pd.DataFrame([{
        'analog_amplitude_saturations': len(event.amplitude_saturated_pixels),
        'trigger_types': event.trigger_type,
        'total_photon_counts': event.photon_stream.photon_count.sum(),
        'times': event.time,
        'zenith_distances': event.zd,
        'azimuths': event.az,
        'ids': event.id,
        }
        for event in run])


def add2ax_photon_count_vs_saturations(
        axis,
        total_photon_counts,
        analog_amplitude_saturations):
    axis.plot(total_photon_counts, analog_amplitude_saturations)
