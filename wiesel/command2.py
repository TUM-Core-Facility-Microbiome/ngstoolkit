import subprocess
import sys
import time

p = subprocess.Popen("""python -c '
from time import sleep ; import sys
for i in range(3):
    sleep(2)
    print "Hello", i
    sys.stdout.flush()
'""", shell=True, stdout=subprocess.PIPE)

while True:
    inline = p.stdout.readline()
    if not inline:
        break
    sys.stdout.write(inline.decode('utf-8'))
    sys.stdout.flush()


time.sleep(2)
print()

inline = p.stdout.readline()
if not inline:
    exit(0)
sys.stdout.write(inline.decode('utf-8'))
sys.stdout.flush()

print("Done")
