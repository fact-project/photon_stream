calling FACT-MARS-CERERS-WHATEVER

```./ceres -f -q --fits --config=ceres.rc -b --out=../run_Mars/ ../photon_stream/photon_stream/tests/resources/cer011014```

calling fact-tools
```java -jar fact-tools-0.18.0.jar ../../photon_stream/photon_stream/production/simulations_pass4.xml -Dinfile=file:../../run_Mars/00000003.014_D_MonteCarlo011_Events.fits -Ddrsfile=file:../src/main/resources/testMcDrsFile.drs.fits.gz -Dout_path_basename=file:../../photon_stream/photon_stream/tests/resources/cer011014```
