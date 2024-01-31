import schedule
import time
from kapital import Kapital


kapital = Kapital()

def my_task():
    kapital.parse()
    print("Executing the task...")

# Schedule the task to run every 5 seconds
schedule.every(5).seconds.do(my_task)

while True:
    schedule.run_pending()
    time.sleep(1)
