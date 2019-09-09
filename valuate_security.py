import financial_calculator


#
# Main script
#

fcf_list = financial_calculator.get_historical_fcf('AAPL', 2010, 2018)

for year, value in sorted(fcf_list.items(), reverse=False):
  print(year, value)






