"""
The magic constants of the photon-stream pass4
"""

TIME_SLICE_DURATION_S = 0.5e-9;
"""
The duration of a single sampling time slice in the photon-stream. This duration
in combination with the fix size integer arrival slice of a photon gives the 
arrival time of the photon.
"""