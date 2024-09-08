import sys
import threading
import time
from datetime import datetime

class ProgressBarThread(threading.Thread):
    def __init__(self, label='Working time:', delay=0.2):
        super(ProgressBarThread, self).__init__()
        self.label = label
        self.delay = delay  # interval between updates
        self.running = False
    def start(self):
        self.running = True
        super(ProgressBarThread, self).start()
    def run(self):
        label = '\r' + self.label + ' '
        while self.running:
            sys.stdout.write("|")
            sys.stdout.flush()
            time.sleep(self.delay)
    def stop(self):
        self.running = False
        self.join()  # wait for run() method to terminate
        sys.stdout.write("\n")
        # sys.stdout.write('\r' + len(self.label)*' ' + '\r')  # clean-up
        sys.stdout.flush()

def work():
    time.sleep(5)  # *doing hard work*

pb_thread = ProgressBarThread('Computing')
pb_thread.start()
work()
pb_thread.stop()
print("The work is done!")