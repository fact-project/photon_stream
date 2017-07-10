import os
from tqdm import tqdm
import pandas as pd
import numpy as np
from multiprocessing.pool import ThreadPool

from . import runinfo
from . import tools


def status(
    photon_stream_dir, 
    max_worker_threads=8
):
    """
    Estimates the production status of FACT events in a 'phs' directory using 
    the FACT run-info-database as a reference.
    Writes a FACT run-info-database to disk with an additional column for the
    number of events found in each run in the 'phs' directory.
    """
    print('Download latest FACT run info ...')
    latest_runinfo = runinfo.download_latest_runinfo()
    latest_number_of_runs = len(latest_runinfo['fRunID'])
    if 'photon_stream_NumTrigger' not in latest_runinfo:
        latest_runinfo['photon_stream_NumTrigger'] = pd.Series(
            np.zeros(latest_number_of_runs, dtype=np.int), 
            index=info.index
        )

    info_path = os.path.abspath(
       os.path.join(photon_stream_dir, 'known_runs.msg')
    )

    try:
        existing_info = runinfo.read_runinfo_from_file(info_path)
        print('Read in existing status info ', info_path)
        print('Update existing status info with latest run info ...')
        for index, row in tqdm(existing_info.iterrows()):
            assert existing_info['fNight'][index] == latest_runinfo['fNight'][index]
            assert existing_info['fRunID'][index] == latest_runinfo['fRunID'][index]
            latest_runinfo.set_value(
                index, 
                'photon_stream_NumTrigger', 
                existing_info['photon_stream_NumTrigger'][index]
            )
    except:
        print('No status info yet, start with latest runinfo ...')
        
    info = latest_runinfo
    
    print('Collect Expected runs ...')
    jobs = []
    for index, row in tqdm(info.iterrows()):
        night = info['fNight'][index]
        run = info['fRunID'][index]

        if info['fRunTypeKey'][index] == runinfo.observation_key:
            if info['photon_stream_NumTrigger'][index] == 0:
                file_name = '{yyyymmnn:08d}_{rrr:03d}.phs.jsonl.gz'.format(
                    yyyymmnn=night,
                    rrr=run
                )

                run_path = os.path.join(
                    photon_stream_dir, 
                    '{yyyy:04d}'.format(yyyy=tools.night_id_2_yyyy(night)), 
                    '{mm:02d}'.format(mm=tools.night_id_2_mm(night)), 
                    '{nn:02d}'.format(nn=tools.night_id_2_nn(night)), 
                    file_name
                )

                jobs.append({
                    'index': index,
                    'night': night,
                    'run': run,
                    'run_path': run_path,
                })

    print('Collect Actual runs ...')
    with ThreadPool(max_worker_threads) as pool:
        number_triggers = pool.map(
            lambda job: triggers_in_photon_stream_run(run_path=job['run_path']),
            jobs
        )        

    print('Save status of Actual runs ...')
    for j, job in tqdm(enumerate(jobs)):
        assert info['fNight'][job['index']] == job['night']
        assert info['fRunID'][job['index']] == job['run']
        info.set_value(
            job['index'], 
            'photon_stream_NumTrigger', 
            number_triggers[j]
        )

    runinfo.write_runinfo_to_file(info, info_path)
    print('Done')


def triggers_in_photon_stream_run(run_path):
    if os.path.exists(run_path):
        number_trigger = tools.number_of_events_in_run(run_path)
        print('Found ', number_trigger, ' in ', run_path)
        return number_trigger
    else:
        return 0


def runs_in_range_str(info, start_night, end_night, max_trigger_rate=200):
    """
    Returns an overview string with a table of all runs in the range between the
    start_night and the end_night.

    Parameters
    ----------
    info                The extended FACT run-info-database of 'known runs'. 
                        Created by photon_stream.production.status.status().

    start_night         The start night to be shown in the table.

    end_night           The end night in the table to be shown. One integer in 
                        format YYYYmmnn. 1-10 decodes the night 'nn', 
                        100-1000 decodes the month 'mm', and 1000-1000000 is the
                        year 'yyyy'.

    max_trigger_rate    Cuts all runs with less then 300*max_trigger_rate events
                        in it.
    """
    past_start = info['fNight'] >= start_night
    before_end = info['fNight'] < end_night
    is_observation_run = info['fRunTypeKey'] == runinfo.observation_key

    rate_below_max_trigger_rate = (
        info['fNumExt1Trigger'] + 
        info['fNumExt2Trigger'] + 
        info['fNumPhysicsTrigger'] + 
        info['fNumPedestalTrigger']) < 300*max_trigger_rate # 300seconds per run

    has_at_least_one_expected_trigger = (
        info['fNumExt1Trigger'] + 
        info['fNumExt2Trigger'] + 
        info['fNumPhysicsTrigger'] + 
        info['fNumPedestalTrigger']) > 0

    valid = (
        past_start&
        before_end&
        is_observation_run&
        rate_below_max_trigger_rate&
        has_at_least_one_expected_trigger)

    night_ids = info['fNight'][valid]
    run_ids = info['fRunID'][valid]
    expected_triggers = (
        info['fNumExt1Trigger'][valid] + 
        info['fNumExt2Trigger'][valid] + 
        info['fNumPhysicsTrigger'][valid] + 
        info['fNumPedestalTrigger'][valid])
    actual_triggers = info['photon_stream_NumTrigger'][valid]
    completation_ratios = actual_triggers/expected_triggers

    out =  ''
    out += 'year month night run '+table_header_str()
    out += '---------------------'+table_line_str()
    for i, run_id in enumerate(run_ids):
        out += '{year:04d}   {month:02d}   {night:02d}   {run:03d} '.format(
            year=tools.night_id_2_yyyy(night_ids.iloc[i]),
            month=tools.night_id_2_mm(night_ids.iloc[i]),
            night=tools.night_id_2_nn(night_ids.iloc[i]),
            run=run_ids.iloc[i])
        out += table_row_str(
            expected_events=int(expected_triggers.iloc[i]),
            actual_events=int(actual_triggers.iloc[i]))
    return out


def overview_str(info, max_trigger_rate=120):
    """
    Returns a short overview string with a table of all events avaiable
    according to the extended FACT run-info-database of 'info'.

    Parameters
    ----------
    info                The extended FACT run-info-database of 'known runs'. 
                        Created by photon_stream.production.status.status().

    max_trigger_rate    Cuts all runs with less then 300*max_trigger_rate events
                        in it.
    """
    is_obs = info['fRunTypeKey'] == runinfo.observation_key

    rate_below_max_trigger_rate = (
        info['fNumExt1Trigger'] + 
        info['fNumExt2Trigger'] + 
        info['fNumPhysicsTrigger'] + 
        info['fNumPedestalTrigger']) < 300*max_trigger_rate # 300seconds per run

    has_at_least_one_expected_trigger = (
        info['fNumExt1Trigger'] + 
        info['fNumExt2Trigger'] + 
        info['fNumPhysicsTrigger'] + 
        info['fNumPedestalTrigger']) > 0

    valid = is_obs&rate_below_max_trigger_rate&has_at_least_one_expected_trigger

    expected_triggers = (
        info['fNumExt1Trigger'][valid] + 
        info['fNumExt2Trigger'][valid] + 
        info['fNumPhysicsTrigger'][valid] + 
        info['fNumPedestalTrigger'][valid])
    actual_triggers = info['photon_stream_NumTrigger'][valid]


    total_expected_events = int(expected_triggers.sum())
    total_actual_events = int(actual_triggers.sum())
    # full overview
    out = ''
    out += 'Photon-Stream for FACT\n'
    out += '----------------------\n'
    out += '\n'
    out += '    from '+str(info['fNight'].min())+' to '+str(info['fNight'].max())+'\n'

    out += '    '+table_header_str()
    out += '    '+table_line_str()
    out += '    '+table_row_str(
        actual_events=total_actual_events, 
        expected_events=total_expected_events)
    out += '\n'

    # full overview
    out += '    by year\n'
    first_year = tools.night_id_2_yyyy(info['fNight'].min())
    last_year = tools.night_id_2_yyyy(info['fNight'].max())
    out += '    year  '+table_header_str()
    out += '    ------'+table_line_str()
    for i in range(last_year - first_year + 1):
        year = first_year + i
        after_start_of_year = info['fNight'] > year*100*100
        before_end_of_year = info['fNight'] < (year+1)*100*100
        is_in_year =  after_start_of_year&before_end_of_year

        expected_triggers_in_year = int((
            info['fNumExt1Trigger'][valid&is_in_year] + 
            info['fNumExt2Trigger'][valid&is_in_year] + 
            info['fNumPhysicsTrigger'][valid&is_in_year] + 
            info['fNumPedestalTrigger'][valid&is_in_year]).sum())
        actual_triggers_in_year = int(info['photon_stream_NumTrigger'][valid&is_in_year].sum())
        out += '    {year:04d}'.format(year=year)
        out += '  '+table_row_str(
            expected_events=expected_triggers_in_year, 
            actual_events=actual_triggers_in_year)
    
    out += '\n'
    out += 'cuts\n'
    out += '----\n'
    out += '- only observation runs (fRunTypeKey == 1)\n'
    out += '- only expected trigger types: [4:physics, 1024:pedestal, 1:ext1, 2:ext2]\n'
    out += '- expected trigger intensity < 300s * '+str(max_trigger_rate)+'Hz\n'
    out += '\n'
    return out


def table_header_str():
    #       0        1         2         3         4          5         6         7    
    #       12345678901234567890123456789012345678901234567898012345678901234567890
    out =  'photon-stream events [#]  recorded events [#]  ratio [%]\n'
    return out 


def table_line_str():
    out =  '--------------------------------------------------------\n'
    return out


def table_row_str(actual_events, expected_events):
    out =  '{actual_events:>24d}  {expected_events:>19d}'.format(
        actual_events=actual_events,
        expected_events=expected_events)+'  '+progress(actual_events/expected_events)+'\n'
    return out    


def progress(ratio, length=20):
    """
    Returns a string with a progress bar e.g. '|||||| 55%'.

    Parameters
    ----------
    ratio       A floating point number between 0.0 and 1.0.

    length      The maximum length of the progress bar '||||' part.
    """
    try:
        prog = int(np.round(ratio*length))
        percent = np.round(ratio*100)
    except ValueError:
        prog = 0
        percent = 0
    out = '|'

    ratio_above_one = False
    if prog > length:
        prog = length
        ratio_above_one = True

    for p in range(prog):
        out += '|'

    if ratio_above_one:
        out += '...'

    out += ' '+str(int(percent))+'%'
    return out