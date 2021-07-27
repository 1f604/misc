# Utility functions

def sort_date_strings(timestamps): # e.g. '2011-06-2', '2011-08-05', '2010-1-14', etc
  timestamps.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
  
def sort_files(fileslist): # sort files or directories by modification time
    results = []
    for path in fileslist:
        mtime = os.stat(path).st_mtime # make sure to give absolute paths to os.stat()
        results.append((mtime, path))
    results.sort()
    return [path for mtime, path in results]
