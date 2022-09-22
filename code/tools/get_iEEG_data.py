from ieeg.auth import Session
import pandas as pd
import pickle
from .clean_labels import clean_labels
from numbers import Number
import numpy as np

def get_iEEG_data(username, pwd, iEEG_filename, start_time_usec, stop_time_usec, select_electrodes=None, ignore_electrodes=None, outputfile=None):
    """
    """
    start_time_usec = int(start_time_usec)
    stop_time_usec = int(stop_time_usec)
    duration = stop_time_usec - start_time_usec

    s = Session(username, pwd)
    ds = s.open_dataset(iEEG_filename)
    all_channel_labels = ds.get_channel_labels()
    all_channel_labels = clean_labels(all_channel_labels)

    if select_electrodes is not None:
        if isinstance(select_electrodes[0], Number):
            channel_ids = select_electrodes
            channel_names = [all_channel_labels[e] for e in channel_ids]
        elif isinstance(select_electrodes[0], str):
            select_electrodes = clean_labels(select_electrodes)
            
            channel_ids = [i for i, e in enumerate(all_channel_labels) if e in select_electrodes]
            channel_names = select_electrodes
        else:
            print("Electrodes not given as a list of ints or strings")

    elif ignore_electrodes is not None:
        if isinstance(ignore_electrodes[0], int):
            channel_ids = [i for i in np.arange(len(all_channel_labels)) if i not in ignore_electrodes]
            channel_names = [all_channel_labels[e] for e in channel_ids]
        elif isinstance(ignore_electrodes[0], str):
            ignore_electrodes = clean_labels(ignore_electrodes)

            channel_ids = [i for i, e in enumerate(all_channel_labels) if e not in ignore_electrodes]
            channel_names = [e for e in all_channel_labels if e not in ignore_electrodes]
        else:
            print("Electrodes not given as a list of ints or strings")

    else:
        channel_ids = np.arange(len(all_channel_labels))
        channel_names = all_channel_labels

    try:
        data = ds.get_data(start_time_usec, duration, channel_ids)
    except Exception as e:
        # clip is probably too big, pull chunks and concatenate
        clip_size = 60 * 1e6

        clip_start = start_time_usec
        data = None
        while clip_start + clip_size < stop_time_usec:
            if data is None:
                data = ds.get_data(clip_start, clip_size, channel_ids)
            else:
                data = np.concatenate(([data, ds.get_data(clip_start, clip_size, channel_ids)]), axis=0)
            clip_start = clip_start + clip_size
        data = np.concatenate(([data, ds.get_data(clip_start, stop_time_usec - clip_start, channel_ids)]), axis=0)

    df = pd.DataFrame(data, columns=channel_names)
    fs = ds.get_time_series_details(ds.ch_labels[0]).sample_rate #get sample rate

    if outputfile:
        with open(outputfile, 'wb') as f:
            pickle.dump([df, fs], f)
    else:
        return df, fs