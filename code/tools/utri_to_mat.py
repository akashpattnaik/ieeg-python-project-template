import numpy as np

def utri_to_mat(utri, n_channels):
    # Have to do column major order since that's how they were saved in MATLAB
    a = np.zeros((n_channels, n_channels))
    triu_cols = []
    triu_rows = []
    for col in range(n_channels):
        for row in range(n_channels):
            if col > row:
                triu_cols.append(col)
                triu_rows.append(row)
    triu_cols = np.array(triu_cols)
    triu_rows = np.array(triu_rows)

    a[(triu_rows, triu_cols)] = utri
    conn_mat = (a + a.T) / (np.eye(n_channels) + 1)

    return conn_mat
