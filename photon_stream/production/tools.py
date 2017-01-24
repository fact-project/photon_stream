import os

def add_runs_path_info(jobs, fact_dir='/fact/'):
    for job in jobs:
        job['yyyy'] = job['NightId'] // 10000
        job['mm'] = (job['NightId'] // 100) % 100
        job['dd'] = job['NightId'] % 100
        job['fact_dir'] = fact_dir
        job['yyyymmdd_dir'] = '/{y:04d}/{m:02d}/{d:02d}/'.format(
            y=run_job['yyyy'],
            m=run_job['mm'],
            d=run_job['dd'])
        job['base_name'] = '{bsn:08d}_{rrr:03d}'.format(
            bsn=job['NightId'],
            rrr=job['RunId'])
        job['raw_file_name'] = job['base_name']+'.fits.fz'
        job['raw_path'] = os.path.join(
            job['fact_dir'], 
            'raw', 
            job['yyyymmdd_dir'], 
            job['raw_file_name'])
        job['aux_dir'] = os.path.join(
            job['fact_dir'], 
            'aux', 
            job['yyyymmdd_dir'])
    return jobs


def jobs_where_path_exists(jobs, path='raw_path'):
    accesible_jobs = []
    for job in jobs:
        if os.path.exists(job[path]):
            accesible_jobs.append(job)
    return accesible_jobs