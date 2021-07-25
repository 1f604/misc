text = "0" * 1000
from pathlib import Path

def createfiles():
    for c in range(8):
        for d in range(8):
            for x in range(20000): 
                Path("/tmp/data3/%01d/%02d/" % (c,d)).mkdir(parents=True, exist_ok=True)
                open("/tmp/data3/%01d/%02d/file%03d.txt" % (c,d,x),"w").write(text)

createfiles()
