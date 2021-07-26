# Utility functions

def sort_date_strings(timestamps): # e.g. '2011-06-2', '2011-08-05', '2010-1-14', etc
  timestamps.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
  return timestamps
