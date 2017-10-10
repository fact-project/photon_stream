import numpy as np
import photon_stream as ps


def random_list_of_lists_event(seed=1337):
    np.random.seed(seed)
    lol = []
    for pixel in range(ps.io.magic_constants.NUMBER_OF_PIXELS):
        time_series = np.random.randint(
            100, 
            size=np.random.randint(10)
        ) + ps.io.magic_constants.NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI
        lol.append(time_series.tolist())
    return lol


def test_repr_lists_of_lists_to_raw_phs():
    lol = random_list_of_lists_event(seed=42)

    raw_phs = ps.representations.list_of_lists_to_raw_phs(lol)
    lol_back = ps.representations.raw_phs_to_list_of_lists(raw_phs)

    for i in range(10):
        print(lol[i])

    print(raw_phs[0:100])

    for pixel in range(len(lol)):
        assert len(lol[pixel]) == len(lol_back[pixel])
        for i in range(len(lol[pixel])):
            assert lol[pixel][i] == lol_back[pixel][i]