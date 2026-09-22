"""Percentile ranks shared by the daily and weekly screeners."""


def pct_rank(values):
    """Rank valid values in [0, 1], using the average rank for ties.

    Missing values retain rank zero; a single valid value is neutral (0.5).
    """
    order = sorted((i for i, value in enumerate(values) if value is not None),
                   key=lambda i: values[i])
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = ((start + end - 1) / 2 / (len(order) - 1)
                if len(order) > 1 else 0.5)
        for i in order[start:end]:
            result[i] = rank
        start = end
    return result
