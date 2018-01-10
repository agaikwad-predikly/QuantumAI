import schedule
import time
import service as sr
def job():
    sr.perform()

#schedule.every().hour.do(job)
schedule.every().day.at("00:10").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)