import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def quarters_range(date_to, date_from=None):
    result = []
    if date_from is None:
        date_from = datetime.datetime.now()
    quarter_from = ((date_from.month / 4) + 1)
    quarter_to = (date_to.month / 4) + 1
    if range(date_to.year, date_from.year) != []:
        for year in range(date_to.year, date_from.year):
            for quarter in range(1, 5):
                if date_from.year == year and quarter <= quarter_from:
                    continue
                result.append([quarter, year])
    else:
        for quarter in range(1, 5):
                year = date_from.year
                result.append([quarter, year])
    return (result)

def quarter_start_end(quarter, year=None):
    """
    Returns datetime.daet object for the start
    and end dates of `quarter` for the input `year`
    If `year` is none, it defaults to the current
    year.
    """
    if year is None:
        year = datetime.datetime.now().year
    d = datetime.date(year, 1+3*(quarter-1), 1)
    return d, d+relativedelta(months=3, days=-1)