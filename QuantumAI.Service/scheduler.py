import schedule
import time
import api_service as sr
import calculation_service as cal_sr
def job():
    sr.perform()
    cal_sr.perform()

schedule.every().day.at("06:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)