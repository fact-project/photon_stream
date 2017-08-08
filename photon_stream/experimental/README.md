# Binary Photon-Stream Format for FACT -- Pass4

## Observation Event
    - Header
    - Observation Event Identifier
    - Observation Information
    - Pointing
    - Photon-Stream
    - Saturated Pixels


## Simulation Event
    - Header
    - Simulation Event Identifier
    - Pointing
    - Photon-Stream
    - Saturated Pixels


### Header (4 Byte)

    uint8
    +--------+
    |VERSION |
    +--------+
    - VERSION == 4 is pass4 

    uint8
    +--------+
    |  Type  |
    +--------+
    - Type == 0 is Observation
    - Type == 1 is Simulation

    uint8
    +--------+
    |   -    |
    +--------+
    future problems 0 (unused so far)

    uint8
    +--------+
    |   -    |
    +--------+
    future problems 1 (unused so far)


### Observation Event Identifier (12 Byte)
        
    uint32
    +--------+--------+--------+--------+
    |              Night Id             |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |               Run Id              |
    +--------+--------+--------+--------+
    
    uint32
    +--------+--------+--------+--------+
    |             Event Id              |
    +--------+--------+--------+--------+
    
### Simulation Event Identifier (12 Byte)

    uint32
    +--------+--------+--------+--------+
    |           CORSIKA RUN Id          |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |         CORSIKA EVENT Id          |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |      CORSIKA Event Reuse Id       |
    +--------+--------+--------+--------+

### Pointing (8 Byte)

    float32
    +--------+--------+--------+--------+
    |   Pointing Zenith Distance [Deg]  |
    +--------+--------+--------+--------+
    
    float32
    +--------+--------+--------+--------+
    |          Pointing Azimuth  [Deg]  |
    +--------+--------+--------+--------+


### Observation Information (12 Byte)

    uint32
    +--------+--------+--------+--------+
    |          UNIX time [s]            |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |      UNIX time [us] mod. [s]      |
    +--------+--------+--------+--------+
    
    uint32
    +--------+--------+--------+--------+
    |            Trigger type           |
    +--------+--------+--------+--------+
    
    
### Photon-Stream  (8 + num. photons + num. pixel Byte)
    
    uint32
    +--------+--------+--------+--------+
    |   Number of pixels and photons    |
    +--------+--------+--------+--------+
    The size of the photon-stream in bytes.


         Photon arrival times in slices 
         (EXAMPLE. The actual shape and structure depent on the specific event)
         uint8 
         +--------+--------+--------+--------+
       0 |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+   
       1 |   XXX  |   XXX  |   255  |
         +--------+--------+--------+ 
       2 |   XXX  |   255  |
         +--------+--------+--------+--------+--------+
       3 |   XXX  |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+--------+--------+--------+ 
       4 |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+--------+--------+--------+   
       5 |   XXX  |   255  |
         +--------+--------+
       6 |   255  |
         +--------+--------+--------+
       7 |   XXX  |   XXX  |   255  |
         +--------+--------+--------+
       .
       .
       .
         +--------+--------+
    1437 |   XXX  |   255  |
         +--------+--------+--------+--------+--------+
    1438 |   XXX  |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+--------+
    1439 |   XXX  |   XXX  |   255  |
         +--------+--------+--------+
    Pixel
    CHID

A list of lists of photon arrival time slices.
The line break from one pixel to the next one is marked by the linebreab 
symbol 2^8-1 = 255. This leaves 255 (0-254) slices to encode arrival times.

### Saturated Pixels (2 + 2 * num. saturated pixel Byte)

    uint16
    +--------+--------+
    |        N        |
    +--------+--------+
    Number of saturated pixels

    uint16
    +--------+--------+--------+--------+     +--------+--------+
    |      CHID 0     |      CHID 1     | ... |      CHID N-1   |
    +--------+--------+--------+--------+     +--------+--------+
    A list of CHIDS of saturated pixels
