import os
import pandas as pd
import numpy as np
import fact


def runs_in_range_str(
    runstatus, 
    start_night=0, 
    end_night=99999999, 
    max_trigger_rate=200
):
    """
    Returns an overview string with a table of all runs in the range between the
    start_night and the end_night.

    Parameters
    ----------
    runstatus           The extended FACT run-info-database of 'runstatus.csv'. 

    start_night         The start night to be shown in the table.

    end_night           The end night in the table to be shown. One integer in 

    max_trigger_rate    Excludes runs above max_trigger_rate events in it.
    """
    rs = runstatus

    past_start = rs['fNight'] >= start_night
    before_end = rs['fNight'] < end_night

    rate_below_max_trigger_rate = rs.NumExpectedPhsEvents < 300*max_trigger_rate # 300seconds per run
    has_at_least_one_expected_trigger = rs.NumExpectedPhsEvents > 0

    valid = (
        past_start&
        before_end&
        rate_below_max_trigger_rate&
        has_at_least_one_expected_trigger
    )

    print(past_start.sum(), before_end.sum(), rate_below_max_trigger_rate.sum(), has_at_least_one_expected_trigger.sum())

    night_ids = rs['fNight'][valid]
    run_ids = rs['fRunID'][valid]
    expected_triggers = rs['NumExpectedPhsEvents'][valid]
    actual_triggers = rs['NumActualPhsEvents'][valid]
    completation_ratios = actual_triggers/expected_triggers

    out =  ''
    out += 'year month night run '+table_header_str()
    out += '---------------------'+table_line_str()
    for i, run_id in enumerate(run_ids):
        out += fact.path.template_to_path(
            night_ids.iloc[i], 
            run_ids.iloc[i], 
            '{Y}   {M}   {D}   {R} '
        )

        if np.isnan(expected_triggers.iloc[i]) or np.isnan(actual_triggers.iloc[i]):
            out += 'nan\n'
        else:
            out += table_row_str(
                expected_events=int(expected_triggers.iloc[i]),
                actual_events=int(actual_triggers.iloc[i])
            )
    return out


def overview_str(runstatus, max_trigger_rate=120):
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
    rs = runstatus
    rate_below_max_trigger_rate = rs.NumExpectedPhsEvents < 300*max_trigger_rate # 300seconds per run
    has_at_least_one_expected_trigger = rs.NumExpectedPhsEvents > 0
    valid = rate_below_max_trigger_rate&has_at_least_one_expected_trigger

    expected_triggers = rs.NumExpectedPhsEvents[valid]
    actual_triggers = rs.NumActualPhsEvents[valid]

    total_expected_events = int(expected_triggers.sum())
    total_actual_events = int(actual_triggers.sum())
    # full overview
    out = ''
    out += 'Photon-Stream for FACT\n'
    out += '----------------------\n'
    out += '\n'
    out += '    from '+str(rs['fNight'].min())+' to '+str(rs['fNight'].max())+'\n'

    out += '    '+table_header_str()
    out += '    '+table_line_str()
    out += '    '+table_row_str(
        actual_events=total_actual_events, 
        expected_events=total_expected_events)
    out += '\n'

    # full overview
    out += '    by year\n'
    first_year = int(fact.path.template_to_path(rs.fNight.min(), 1, '{Y}'))
    last_year = int(fact.path.template_to_path(rs.fNight.max(), 1, '{Y}'))
    out += '    year  '+table_header_str()
    out += '    ------'+table_line_str()
    for i in range(last_year - first_year + 1):
        year = first_year + i
        after_start_of_year = rs['fNight'] > year*100*100
        before_end_of_year = rs['fNight'] < (year+1)*100*100
        is_in_year =  after_start_of_year&before_end_of_year

        expected_triggers_in_year = int(rs.NumExpectedPhsEvents[valid&is_in_year].sum())
        actual_triggers_in_year = int(rs.NumActualPhsEvents[valid&is_in_year].sum())
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
    out =  'phs-events           [#]  raw-events      [#]  ratio [%]\n'
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
