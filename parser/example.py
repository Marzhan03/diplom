import schedule
import time
from eadaily import EaDaily


eadaily = EaDaily()

def my_task():
    eadaily.parse()
    print("Executing the task...")

# Schedule the task to run every 5 seconds
schedule.every(5).seconds.do(my_task)

while True:
    schedule.run_pending()
    time.sleep(1)
