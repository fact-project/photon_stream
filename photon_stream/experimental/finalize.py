
def finalize_jsonl2binary(
    inpath, 
    outpath, 
    truncate_photon_stream=False, 
    drop_baselinses=False):

    fin = JsonLinesGzipReader(inpath)
    first_evt_in = reduce_event(fin.__next__())
    run_id = first_evt_in['RunId']
    night_id = first_evt_in['NightId']
    fin = JsonLinesGzipReader(inpath)

    with open(outpath, 'wb') as fout:
        # Run HEADER
        append_uint64(night_id, fout)
        append_uint64(run_id, fout)

        for evt_in in fin:

            evt_in = reduce_event(
                evt_in=evt_in,
                truncate_photon_stream=truncate_photon_stream,
                drop_baselinses=drop_baselinses)

            # Event HEADER
            append_uint32(evt_in['EventId'], fout)
            append_uint32(evt_in['TriggerType'], fout)
            append_uint32(evt_in['UnixTimeUTC'][0], fout)
            append_uint32(evt_in['UnixTimeUTC'][1], fout)
            append_float32(evt_in['AzPointing'], fout)
            append_float32(evt_in['ZdPointing'], fout)
            ps = read_photonstream_from_raw_photonstream(
                raw_photon_stream=evt_in['PhotonStream'], 
                slice_duration=0.5e-9)
            append_photonstream_to_binary_file(ps, fout)

            if 'BaseLines' in evt_in:
                append_baselines(evt_in['BaseLines'], fout)


def append_uint32(number, fout):
    fout.write(np.uint32(number).tobytes())


def append_uint64(number, fout):
    fout.write(np.uint64(number).tobytes())


def append_float32(float_number, fout):
    fout.write(np.float32(float_number).tobytes())


def append_baselines(baselines, fout):
    fout.write(np.array(baselines, dtype=np.int16).tobytes())