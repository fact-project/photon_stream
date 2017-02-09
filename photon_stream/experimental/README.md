# Binary Photon-Stream Format for FACT -- Pass4


### Event Header
    
    Night Id
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+

    Run Id
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+
    
    Event Id
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+
    
    UNIX time seconds
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+

    UNIX time micro seconds
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+
    
    Trigger type
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+
    
    Pointing Zenith Distance
    float32
    +--------+--------+--------+--------+
    |FFFFFFFF|FFFFFFFF|FFFFFFFF|FFFFFFFF|
    +--------+--------+--------+--------+
    
    Pointing Azimuth
    float32
    +--------+--------+--------+--------+
    |FFFFFFFF|FFFFFFFF|FFFFFFFF|FFFFFFFF|
    +--------+--------+--------+--------+
    
    
### Photon-Stream Header

    Slice time duration
    float32
    +--------+--------+--------+--------+
    |FFFFFFFF|FFFFFFFF|FFFFFFFF|FFFFFFFF|
    +--------+--------+--------+--------+

    Number of pixels plus number of photons 
    (the size of the photon-stream in bytes)
    uint32
    +--------+--------+--------+--------+
    |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
    +--------+--------+--------+--------+


### Photon-Stream

         Photon arrival times in slices
         uint8 
         +--------+--------+--------+--------+
       0 |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+   
       1 |   XXX  |   XXX  |   256  |
         +--------+--------+--------+ 
       2 |   XXX  |   256  |
         +--------+--------+--------+--------+--------+
       3 |   XXX  |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+--------+--------+--------+ 
       4 |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+--------+--------+--------+   
       5 |   XXX  |   256  |
         +--------+--------+
       6 |   256  |
         +--------+--------+--------+
       7 |   XXX  |   XXX  |   256  |
         +--------+--------+--------+
       .
       .
       .
         +--------+--------+
    1437 |   XXX  |   256  |
         +--------+--------+--------+--------+--------+
    1438 |   XXX  |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+--------+
    1439 |   XXX  |   XXX  |   256  |
         +--------+--------+--------+
    Pixel
    CHID

### Saturated Pixels

    Number of saturated pixels
    uint16
    +--------+--------+
    |        N        |
    +--------+--------+

    CHIDS of saturated pixels
    uint16
    +--------+--------+--------+--------+     +--------+--------+
    |      CHID 0     |      CHID 1     | ... |      CHID N-1   |
    +--------+--------+--------+--------+     +--------+--------+