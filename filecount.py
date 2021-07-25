import os, time
from time import sleep
import shutil
from collections import deque
import os

filecount = 0

def iterate(path):
    global filecount
    dirlist = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                dirlist.append(entry)
            else:
                filecount += 1
    return dirlist


def countfiles(dir = '/tmp/data2'):
    dirlist = [dir]
    while True:
        if not dirlist:
            break
        directory = dirlist.pop()
        newdirs = iterate(directory)
        dirlist.extend(newdirs)
    
start = time.time()
countfiles()
print("total files:", filecount)
end = time.time()
print(end - start)
