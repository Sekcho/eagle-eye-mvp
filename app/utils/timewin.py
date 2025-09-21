from typing import List, Tuple

def top_contiguous_block(values: list, block_hours: int = 2) -> Tuple[int, float]:
    """Return (start_hour, avg_value) maximizing the average over a contiguous block."""
    n = len(values)
    best_h, best_val = 0, -1.0
    for h in range(0, n - block_hours + 1):
        avg = sum(values[h:h+block_hours]) / block_hours
        if avg > best_val:
            best_val, best_h = avg, h
    return best_h, best_val
