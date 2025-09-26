# bollinger.py

import numpy as np

def add_bollinger_bands(data, window=20):
    """Add Bollinger Bands columns to DataFrame"""
    # MA and Rolling Std
    data['MA_20'] = data['Close'].rolling(window=window, min_periods=1).mean()
    data['BB_Upper'] = data['MA_20'] + 2 * data['Close'].rolling(window=window, min_periods=1).std()
    data['BB_Lower'] = data['MA_20'] - 2 * data['Close'].rolling(window=window, min_periods=1).std()
    return data

def detect_bband_big_moves(data):
    """Detect big moves outside Bollinger Bands"""
    big_move_above = data[data['Close'] > data['BB_Upper']]
    big_move_below = data[data['Close'] < data['BB_Lower']]
    bolli_big_moves = len(big_move_above) + len(big_move_below)
    return {
        'bolli_big_moves': bolli_big_moves,
        'big_move_above_count': len(big_move_above),
        'big_move_below_count': len(big_move_below),
        'indices_above': big_move_above.index.tolist(),
        'indices_below': big_move_below.index.tolist()
    }
