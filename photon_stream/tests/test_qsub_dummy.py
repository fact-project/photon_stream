import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources

def test_output_path_extraction_from_worker_job():
    with tempfile.TemporaryDirectory(prefix='photon_stream_test_qsub') as tmp:        
        job_path = os.path.join(tmp, 'worker_job.sh')
        out_dir = '/home/photon_stream/YYYY/mm/dd/'
        out_base_name = 'YYYYmmdd_RRR'

        ps.production.write_worker_script(
            path=job_path,
            out_dir=out_dir,
            out_base_name=out_base_name)

        out_dir, out_base_name = ps.production.dummy_qsub.extract_out_path_from_worker_job(
            job_path)
        out_path = os.path.join(out_dir, out_base_name)

        assert out_path == os.path.join(out_dir, out_base_name)