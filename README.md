# The Photon Stream
The photon stream is based on the [single photon extractor](https://github.com/fact-project/single_photon_extractor). The events of the FACT Imaging Atmospheric Cherenkov Telecope (IACT) can be represented as photon stream using the single photon extractor.
In a photon stream, the single photon arrival times are stored for each read out channel (image pixel).

## Install
```bash
pip install git+https://github.com/fact-project/photon_stream
```

## Python API
```python
import photon_stream as ps
run = ps.fact.Run('20150123_020.json.gz')
event = run[0]
event.plot()
```
![img](example/example_event_small.gif)

## Where to go from here
- explore an intermediate file format based on the photon stream, only photons no noise
- explore novel image cleaning by combining the temporal and directional information of all pixels before cutting (DBSCAN clustering)
