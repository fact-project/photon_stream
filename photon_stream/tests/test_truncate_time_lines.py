import photon_stream as ps

def test_time_line_truncation_manual():

    a_photon_stream = ps.PhotonStream(
        time_lines=[
            [0, 1, 2,  3,  4,  5,  6,  7,  8,  9, 10],
            [5, 6, 7,  8,  9, 10, 11, 12, 13, 14, 15],
            [7, 8, 9, 10, 11, 12],
        ],
        slice_duration=1.
    )

    truncated_photon_stream = a_photon_stream.truncated_time_lines(
        start_time=6,
        end_time=11)

    assert truncated_photon_stream.time_lines[0] == [6, 7, 8, 9, 10]
    assert truncated_photon_stream.time_lines[1] == [6, 7, 8, 9, 10]
    assert truncated_photon_stream.time_lines[2] == [7, 8, 9, 10]
