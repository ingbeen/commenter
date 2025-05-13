import time
import random

def wait_random(min_sec=1.0, max_sec=3.0):
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)