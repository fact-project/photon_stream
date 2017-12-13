import photon_stream as ps
import numpy as np


def non_saturated_raw_phs():
    return 255*np.ones(
        ps.io.magic_constants.NUMBER_OF_PIXELS,
        dtype=np.uint8
    )


def saturated_raw_phs():
    LIMIT = ps.io.magic_constants.NUMBER_OF_PHOTONS_IN_PIXEL_BEFORE_SATURATION
    pixel_CHID_with_saturation = 137
    return np.array(
        np.arange(pixel_CHID_with_saturation).tolist() +
        np.ones(LIMIT).tolist() +
        np.arange(
            pixel_CHID_with_saturation,
            ps.io.magic_constants.NUMBER_OF_PIXELS
        ).tolist(),
        dtype=np.uint8
    )


def test_adc_not_saturated():
    phs = ps.PhotonStream()
    phs.saturated_pixels = np.arange(0)
    assert not phs._is_adc_saturated()


def test_adc_is_saturated():
    phs = ps.PhotonStream()
    phs.saturated_pixels = np.arange(1)
    assert phs._is_adc_saturated()


def test_extractor_not_saturated():
    phs = ps.PhotonStream()
    phs.raw = non_saturated_raw_phs()
    assert not phs._is_single_pulse_extractor_saturated()


def test_extractor_is_saturated():
    phs = ps.PhotonStream()
    phs.raw = saturated_raw_phs()
    assert phs._is_single_pulse_extractor_saturated()


def test_saturation_no_adc_no_extractor():
    phs = ps.PhotonStream()
    phs.saturated_pixels = np.arange(0)
    phs.raw = non_saturated_raw_phs()
    assert not phs.is_saturated()


def test_saturation_is_adc_no_extractor():
    phs = ps.PhotonStream()
    phs.saturated_pixels = np.arange(1)
    phs.raw = non_saturated_raw_phs()
    assert phs.is_saturated()


def test_saturation_no_adc_is_extractor():
    phs = ps.PhotonStream()
    phs.saturated_pixels = np.arange(0)
    phs.raw = saturated_raw_phs()
    assert phs.is_saturated()


def test_saturation_is_adc_is_extractor():
    phs = ps.PhotonStream()
    phs.saturated_pixels = np.arange(1)
    phs.raw = saturated_raw_phs()
    assert phs.is_saturated()
