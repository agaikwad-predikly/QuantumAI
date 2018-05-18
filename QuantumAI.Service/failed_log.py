import database as db

def save_job_status(log_id,job_id,ticker_id,status, retry_count,total_process_count,success_count,failed_count,job_date,job_start_date,job_end_date):
	job_details=db.call_procedure("insert_update_fail_log_status_details",[log_id,job_id,ticker_id, status, retry_count,total_process_count,success_count,failed_count,job_date,job_start_date,job_end_date])
	

def save_error_log_details(log_id, job_id, ticker_id, api_id,period, period_year, period_quarter,period_date, status, retry_count, job_date, job_start_date, job_end_date,error):
	error_details=db.call_procedure("insert_update_fail_log_error_details",[log_id, job_id, ticker_id, api_id,period, period_year, period_quarter,period_date.date(), status, retry_count, job_date, job_start_date, job_end_date,error])
