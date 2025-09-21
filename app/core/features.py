def pattern_score(popularity_0_100: float) -> float:
    return float(popularity_0_100 or 0.0)

def historical_score(hit_rate_0_1: float) -> float:
    return 100.0 * float(hit_rate_0_1 or 0.0)

def travel_score(bucket: str) -> float:
    # e.g., <=10min:1.0, 10-20:0.8, >20:0.6 -> rescale to 0-100
    mapping = {"short": 100, "mid": 80, "long": 60}
    return float(mapping.get(bucket, 80))
