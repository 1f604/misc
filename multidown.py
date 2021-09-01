#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    import multidown
    multidown.download_urls([("http://google.com", "goog.html"), 
                             ("http://amazon.com", "amaz.html")])

    multidown.download_urls(["http://google.com", "http://amazon.com"])
    
Parameters:
    def download_urls(url_dests: list, destdir = 'downloaded_by_multidown', 
                      timeout=3, retries=5, thread_count=50)
    
Created on Wed Dec 5 2018
@author: 1f604
"""

import threading, queue, os, urllib, logging
from queue import Queue
from pprint import pprint
from urllib.request import urlopen

logging.basicConfig(level=logging.WARNING)

# unfortunately, some websites won't play nice if you don't fake your user-agent
headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}

log = logging.getLogger('multidown')

def get_file(url):
    remaining_download_tries = 5
    while remaining_download_tries > 0:
        try:
            request = urllib.request.Request(url, headers=headers)
            with urlopen(request, timeout = 5) as response:
                contents = response.read()
            log.info("Successfully fetched: "+url)
            return contents
        except Exception as e:
            log.warning("Failed to download: "+url+" got exception: "+str(e))
            if remaining_download_tries > 1:
                log.warning("Retrying for url: "+url)
        remaining_download_tries -= 1
    log.error("Maximum retries reached for url: "+ url)


class DownloaderThread(threading.Thread):
    """ Downloads urls into files with set timeout and retries on error.
        Input is done by placing (url, dest) tuples into url_q. 
        Output is done by placing url into failed_q. 
        If download is successful, nothing is placed onto failed_q. 
    """
    def __init__(self, url_q: Queue, failed_q: Queue, timeout=3, retries=5):
        super().__init__()
        self.failed_q = failed_q
        self.url_q = url_q
        self.timeout = timeout
        self.retries = retries
        
    def download_file(self, url, dest):
        # Note: Will fail if dest is not a valid filename
        """ downloads url into dest (filename with full path) with retry
            if failed to download url, puts url into failed_q
        """
        remaining_download_tries = self.retries + 1
        while remaining_download_tries > 0:
            try:
                request = urllib.request.Request(url, headers=headers)
                with urlopen(request, timeout = self.timeout) as response:
                    contents = response.read()
                with open(dest, 'wb') as f:
                    f.write(contents)
                log.info("Successfully downloaded: "+url)
                return
            except Exception as e:
                log.warning("Failed to download: "+url+" got exception: "+str(e))
                if remaining_download_tries > 1:
                    log.warning("Retrying for url: "+url)
            remaining_download_tries -= 1
        log.error("Maximum retries reached for url: "+ url)
        self.failed_q.put(url)
    
    def run(self):
        """ repeatedly get an url from url_q and download it
            finishes when url_q is empty
        """
        while True:
            try:
                url, dest = self.url_q.get(block=False)
                self.download_file(url, dest)
            except queue.Empty:
                break

def download_urls(url_dests: list, destdir = 'downloaded_by_multidown', timeout=3, retries=5, thread_count=50):
    """ Precondition:
          url_dests is either a list of urls: [str]
          or a list of (url, filename) tuples: [(str, str)]
        Returns the list of urls that were not downloaded. 
    """
    # if no filenames given, generate filenames as appropriate
    log.info(url_dests)
    if type(url_dests[0]) is str:
        destdir = os.path.join(destdir, '')
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        url_dests = [(url, destdir + os.path.basename(url)) for url in url_dests]
        log.warning("filenames were not supplied so they were generated from the URLs")
        
    # create the queues and input the urls to be downloaded
    url_q = Queue()
    failed_q = Queue()
    for url_dest in url_dests:
        url_q.put(url_dest)
        
    # create the thread pool
    pool = [DownloaderThread(url_q=url_q, failed_q=failed_q, 
                             timeout=timeout, retries=retries)
                                    for _ in range(thread_count)]
    # start all threads
    for thread in pool:
        thread.daemon = True
        thread.start()    
    print("All threads in threadpool started")
    
    # now get results 
    for thread in pool:
        thread.join()
        
    print("All downloader threads finished.")
    failed_urls = list(failed_q.queue)
    if failed_urls:
        print("Some urls could not be downloaded:")
        pprint(failed_urls)
    else:
        print("All urls were successfully downloaded.")
    return failed_urls

def main():
    dus = []
#    dus.append(("http://www.google.com", "a/goog.html"))
#    dus.append(("http://www.amazon.com", "b/amaz.html"))
#    dus.append(("http://www.amazon.com", "amaz.html"))
    dus.append("http://www.google.com")
    dus.append("http://www.amazon.com")
    dus.append("http://www.amazon.com")
#    dus.append(("https://ars.els-cdn.com/content/image/1-s2.0-S0308814616314601-mmc1.pdf", "asd.pdf"))
    print(download_urls(dus, destdir="downtest", retries=1))

if __name__ == "__main__":
    main()
