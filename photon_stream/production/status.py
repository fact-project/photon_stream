import os
from tqdm import tqdm
import pandas as pd
import numpy as np

from . import runinfo
from . import tools


def number_of_events_in_run(run_path):
    """
    Returns the number of lines inside a gzipped text file.
    """
    ps = subprocess.Popen(['zcat', run_path], stdout=subprocess.PIPE)
    wc_out = subprocess.check_output(('wc', '-l'), stdin=ps.stdout)
    ps.wait()
    return int(wc_out)


def status(photon_stream_dir, known_runs_database='known_runs.msg'):
    """
    Estimates the avaiability status of FACT events in a 'phs' directory using 
    the FACT run-info-database as a reference.
    Writes a FACT run-info-database to disk with additional columns for the
    number of events found in each run in the 'phs' directory.
    """
    info_path = os.path.abspath(
	os.path.join(photon_stream_dir, known_runs_database))
    try:
        info = runinfo.read_runinfo_from_file(info_path)
    except:
        info = runinfo.download_latest_runinfo()

    if 'photon_stream_NumTrigger' not in info:
        info['photon_stream_NumTrigger'] = pd.Series(
            np.zeros(len(info['fRunID']), 
            dtype=np.int), 
            index=info.index
        )

    for index, row in tqdm(info.iterrows()):
        night = info['fNight'][index]
        run = info['fRunID'][index]

        if info['fRunTypeKey'][index] == runinfo.OBSERVATION_RUN_TYPE_KEY:
            if info['photon_stream_NumTrigger'][index]==0:
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

                if os.path.exists(run_path):    
                    info.set_value(
                        index, 
                        'photon_stream_NumTrigger', 
                        number_of_events_in_run(run_path)
                    )
                    print(
                        'New run '+str(night)+' '+str(run)+' '+
                        str(info['photon_stream_NumTrigger'][index])+
                        ' trigger.'
                    )

    runinfo.write_runinfo_to_file(info, info_path)


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
    is_observation_run = info['fRunTypeKey'] == runinfo.OBSERVATION_RUN_TYPE_KEY

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
        has_at_least_one_expected_trigger
    )

    night_ids = info['fNight'][valid]
    run_ids = info['fRunID'][valid]
    expected_triggers = (
        info['fNumExt1Trigger'][valid] + 
        info['fNumExt2Trigger'][valid] + 
        info['fNumPhysicsTrigger'][valid] + 
        info['fNumPedestalTrigger'][valid]
    )
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
            run=run_ids.iloc[i]
        )
        out += table_row_str(
            expected_events=int(expected_triggers.iloc[i]),
            actual_events=int(actual_triggers.iloc[i])
        )
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
    is_obs = info['fRunTypeKey'] == runinfo.OBSERVATION_RUN_TYPE_KEY

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
        info['fNumPedestalTrigger'][valid]
    )
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
            info['fNumPedestalTrigger'][valid&is_in_year]).sum()
        )
        actual_triggers_in_year = int(
            info['photon_stream_NumTrigger'][valid&is_in_year].sum()
        )
        out += '    {year:04d}'.format(year=year)
        out += '  ' + table_row_str(
            expected_events=expected_triggers_in_year, 
            actual_events=actual_triggers_in_year
        )
    
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


def strip_runinfo_for_photon_stream_status_inplace(runinfo):
    keys_to_keep = [
        'fNight',
        'fRunID',
        'fNumExt1Trigger',
        'fNumExt2Trigger',
        'fNumPhysicsTrigger', 
        'fNumPedestalTrigger',
        'fRunTypeKey',
        'photon_stream_NumTrigger'
    ]
    for key in keys_to_keep:
        assert key in runinfo
	
    cols_to_drop = []
    for key in runinfo.keys():
        if key not in keys_to_keep:
            runinfo.drop(key, axis=1, inplace=True)

    runinfo = runinfo[runinfo['fRunTypeKey'] == runinfo.OBSERVATION_RUN_TYPE_KEY]
    
