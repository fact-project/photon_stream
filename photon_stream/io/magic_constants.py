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
NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI = 30
"""
The offset of the FACT ROI start slice to the photon-stream output winow start 
slice.

                        whole time series
 |.......................................................................|
 |                                                                       |
 |         |................ extraction window .................|        |
 |         | <---------- length = 225 ------------------------> |        |
 |         |                                                    |        |
 |         |       |.. output window ..|                        |        |
 0        20       | <- length=100 ->  |                       245      300
                  30                  130

[in 2GHz slices]

- whole time series
    The full 300 slices (150ns) Region Of Interest (ROI) of the FACT camera.

- extraction window
    The timewindow where single pulses are searched for and extracted.

- output window
    The photon-stream output time window 100 slices (50ns)

see also: https://github.com/fact-project/fact-tools/blob/master/src/main/java/fact/photonstream/SinglePulseExtraction.java
"""
NUMBER_OF_TIME_SLICES = 100
"""
See figure above.
"""
NUMBER_OF_PIXELS = 1440
"""
Number of independent read out picture cells in the FACT camera.
"""
NUMBER_OF_PHOTONS_IN_PIXEL_BEFORE_SATURATION = 500
"""
When there are 500 photons in a pixel, this pixel is saturated. The single pulse
extraction stops after 500 extractions.
"""