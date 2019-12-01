# How does this work
The entry point to the financial calculator is the ```valuate_security.py``` script. It takes two inputs, a ticker symbol and a fiscal year. So for example:

```python valuate_security.py -ticker aapl 2018```

Will estimate the intrinsic price for AAPL as of fiscal year end 2018 using a discount cash flow analysis.

It's output is a report containing the results of the calculation.

Calculations are referred to as "models" throughout this project. Each model uses the same DCF formula to calculate its intrinsic price, but varies in terms of how it forecasts its free cash flows and discount rates. Models download historical financial statements from a data provider (currently "Intrinio"), and use it as inputs to their calculations.

## Models
All models (as of this version there is only one) are derived from an abstract class called ```BaseDCFModel``` which has the following characteristics:

1) Sets the discount rate to a constant 9.75%
2) Sets long term growth rate (used for terminal value) to a constant 2.5%
3) Historical look-back is set to 4 years
4) Short term forecasts extend to 4 years in the future, after which a terminal value is applied.

It also provides a way to all store and retrieve all intermediate results, which are used for both testing as well report generation.

Here is a condensed version of the ```BaseDCFModel``` class

```python
class BaseDCFModel(ABC):
  """
  Base class for all DCF Models.
  The current implementation supports the following features:
  1) A consistent method to compute the DCF price
  2) A dictionary of intermediate results that can be used
  for debugging purpose
  """

  intermediate_results = {}

  @abstractmethod
  def calculate_dcf_price(self):
    """
    Calculates the DCF Price of a security.
    See implementing classes for details.
    """
    pass

  ...

  def get_itermediate_results(self):
    return self.intermediate_results
    
  ...
```

### The Jimmy Model
This model is based on this tutorial: (https://www.youtube.com/watch?v=fd_emLLzJnk&t=500s), which was taken from a YouTube series called "Learn to Invest".

The approach for this model is fairly simple. Historical revenues are used to estimate future revenue growth, and then a series of multipliers (also based on history) are used to go from revenue forecasts to free cash flow forecasts.

These are the exact steps:

1) Generate 4 years of historical free cash flow to equity
2) Generate 4 years of historical net income
3) Determine the FCFE / net income ratio and choose the median value.
4) Generate 4 years of historical revenue. Determine median growth, and forecast the next 4 years. The video suggests using two years of analyst forecast. Here we use the historical median.
5) Determine historical profit margin (net margin) by dividing net income
by revenue and choosing the median value.
6) Forecast net income by multiplying revenue by profit margin
7) Forecast FCFE by multiplying net income by the number determined in step 3.
8) Apply the DCF analysis using free cash flow forecasts, growth estimate and
discount rates.

## Financial Data
All financial data is sourced externally using an API from "Intrinio", though other providers could also be added.

This is implemented in the ```data_provider``` package, specifically ```intrinio_data.py``` and is used directly by the model classes that perform
the calculations.

### Caching
Data is also cache locally using an opensource pacakge called ```diskcache``` which offers a SQLite based cache. More information can be found here: (https://github.com/grantjenks/python-diskcache)

Though it is referred to as a cache, the data is never purged since all of it is considered immutable. To delete or reset the contents of the cache, simply delete entire ```./financial-data/``` folder

## Reports
Reports are spreadsheet based, where each worksheet contains the output of a different model. Reports have the ability to contain one or more worksheets though currently they only use one.

The main reporting object is called ```WorkbookReport```. This class is responsible for assembling the various worksheets and saving the final report. It must contain one or more ```ReportWorksheet``` derived worksheets that are coupled to a specific model.

```ReportWorksheet``` objects perform two tasks:
1) They load a template xlsx spreadsheet that represents the specific report and includes the appropriate layout and formatting
2) They update it with the appropriate results and save it as a sepatare worksheet in the final report.

Here is an example:

```python
from reporting.workbook_report import WorkbookReport
from reporting.jimmy_report_worksheet import JimmyReportWorksheet
from exception.exceptions import ValidationError, ReportError 

report = WorkbookReport(None)

report.add_worksheet(JimmyReportWorksheet(), "Jimmy DCF", JimmyDCFModel('aapl', 2018))

try:
  report.generate_report('output.xlsx')
except ReportingError as re:
  print(re)
```

Reporting is based on the ```openpyxl``` package which can be found here:
(https://openpyxl.readthedocs.io/en/stable/)

## Exceptions
All low level exceptions are wrapped into one of a handful of application exceptions defined in ```exception.exceptions```

This table details their use:

|Exception Name|Description|
|---|---|
|BaseError|The base exception for all custom exceptions|
|ValidationError|Raised whenever bad inputs are supplied|
|DataError|A wrapper exception for all data provider errors|
|CalculationError|Raised whenever a calculation could not be performed because the supplied inputs don't make sense|
|ReportError|A wrapper exception for all openpyxl errors|
|FileSystemError|Raised whenever there is an error interacting with the filesystem, for example if a cache or reporting directory cannot be created|
