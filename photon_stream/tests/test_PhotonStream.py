import photon_stream as ps
import pkg_resources

def test_properties():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    event = next(ps.ObservationReader(run_path))

    assert event.photon_stream.number_photons == 4984
    assert event.photon_stream.flatten().shape == (4984, 3)
    assert event.photon_stream.min_arrival_slice == 30
    assert event.photon_stream.max_arrival_slice == 129


def test_can_truncate_itself():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    event = next(ps.ObservationReader(run_path))
    event.photon_stream.truncated_time_lines(30e-9, 130e-9)


def test_time_line_truncation_manual():
    time_lines = [
        [0,1,2,3,4,5,6,7,8,9,10],
                  [5,6,7,8,9,10,11,12,13,14,15],
                      [7,8,9,10,11,12]]

    phs = ps.PhotonStream(time_lines=time_lines, slice_duration=1.0)

    phs._truncate_time_lines(start_time=6, end_time=11)

    assert phs.time_lines[0] == [6,7,8,9,10]
    assert phs.time_lines[1] == [6,7,8,9,10]
    assert phs.time_lines[2] ==   [7,8,9,10]