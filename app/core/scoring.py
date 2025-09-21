def opportunity_score(pattern: float, historical: float, context: float = 70.0, travel: float = 80.0,
                      w=(0.45, 0.35, 0.10, 0.10)) -> float:
    p, h, c, t = pattern, historical, context, travel
    w1, w2, w3, w4 = w
    score = w1*p + w2*h + w3*c + w4*t
    return round(score, 2)
