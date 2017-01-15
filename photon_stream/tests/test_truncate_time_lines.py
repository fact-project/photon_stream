import photon_stream as ps

def test_time_line_truncation_manual():

    time_lines = [
        [0,1,2,3,4,5,6,7,8,9,10],
                  [5,6,7,8,9,10,11,12,13,14,15],
                      [7,8,9,10,11,12]]

    trunc_time_lines = ps.truncate_time_lines(
        time_lines=time_lines,
        slice_duration=1.0,
        start_time=6, 
        end_time=11)

    assert trunc_time_lines[0] == [6,7,8,9,10]
    assert trunc_time_lines[1] == [6,7,8,9,10]
    assert trunc_time_lines[2] ==   [7,8,9,10]