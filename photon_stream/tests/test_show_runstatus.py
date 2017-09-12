import photon_stream as ps


def test_status_bar_string():
    progress = ps.production.show_runstatus.progress

    progress_bar_str = progress(ratio=0.0, length=50)
    assert len(progress_bar_str) < 50

    progress_bar_str = progress(ratio=1.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 60    

    progress_bar_str = progress(ratio=10.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 61  

    progress_bar_str = progress(ratio=100.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 62 