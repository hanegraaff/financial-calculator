from datetime import datetime
from datetime import timedelta
from exception.exceptions import ValidationError

def get_fiscal_year_period(year : int, extend_by_days : int):
  """
    returns the first and last day of a year's fiscal period.
    For example:
      2018 -> ('2018-01-01', '2019-12-31')

    the end date can be extended by "extend_by_days"
    For example:
      (2018, 10) -> ('2018-01-01', '2019-01-10')

    Parameters
    ----------
    year : int
      the fiscal year in question
    extend_by_days : int
      number of days by which to extend the fiscal period.
      This is done to account for the fact that financial statements may be submitted
      shortly after the fiscal period ends 
    
    Returns
    -----------
    A tuple of strings containing the start and end date of the fiscal period
  """
  if year < 2000:
    raise ValidationError("Invalid Date. Must be >= 2000", None)

  if extend_by_days < 0 or extend_by_days > 350:
    raise ValidationError("Invalid extend_by_days. Must between 0 and 350", None)

  start = datetime(year, 1, 1)
  end = datetime(year, 12, 31) +  timedelta(days=extend_by_days)
  return(date_to_string(start), date_to_string(end))


def date_to_string(date : object):
  """
    returns a string representation of a date that is usable by the intrinio API

    Parameters
    ----------
    date : object
      the date in question

    Returns
    ----------
    A string formatted as YYYY-MM-DD. This is the format used by most Intrinio APIs
  """    
  return date.strftime("%Y-%m-%d")
