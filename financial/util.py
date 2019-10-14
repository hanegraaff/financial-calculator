from datetime import datetime
from datetime import timedelta
from exception.exceptions import ValidationError

def get_fiscal_year_period(date : int, extend_by_days : int):
  """
    returns the first and last day of a year's fiscal period.
    For example:
      2018 -> ('01-01-2018', '12-31-2018)

    the end date can be extended by "extend_by_days"
    For example:
      (2018, 10) -> ('01-01-2018', '01-10-2019)
  """
  if date < 2000:
    raise ValidationError("Invalid Date. Must be >= 2000", None)

  if extend_by_days < 0 or extend_by_days > 350:
    raise ValidationError("Invalid extend_by_days. Must between 0 and 350", None)

  start = datetime(date, 1, 1)
  end = datetime(date, 12, 31) +  timedelta(days=extend_by_days)
  return(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
