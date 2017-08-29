"""
The magic constants of the photon-stream pass4
"""

TIME_SLICE_DURATION_S = 0.5e-9;
"""
The duration of a single sampling time slice in the photon-stream. This duration
in combination with the fix size integer arrival slice of a photon gives the 
arrival time of the photon.
"""
SINGLEPULSE_EXTRACTOR_PASS = 4
"""
The version of the fact-tools single pulse extractor. This version number
just happens to be the fourth iteration of the extractor whic is the first one 
used for mass production.
It corresponds to fact-tools version 0.18.0 onwards until there are changes 
to the extractor.
"""