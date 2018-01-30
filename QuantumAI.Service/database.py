import sys
import psycopg2

def get_connection_string():
	return "host=quantum-ai-db.cqmxufpxd5v3.us-west-1.rds.amazonaws.com dbname=quantum_ai_db user=quantum_admin password=Quantum#456"
#	return "host=localhost dbname=quantum_ai_db user=postgres password=root"

def flatten(l):
    return map(lambda x: x[0], l)

def get_data(query):
	connection_string=get_connection_string()
	conn = psycopg2.connect(connection_string)
	ncurs = conn.cursor('csr')
	ncurs.execute(query)
	data =  ncurs.fetchall()
	ncurs.close()
	conn.commit()
	return data

def call_procedure(procedure_name, params):
	connection_string=get_connection_string()
	conn = psycopg2.connect(connection_string)
	try:
		ncurs = conn.cursor()
		ncurs.callproc(procedure_name,params)
		row = ncurs.fetchall()
		ncurs.close()
		conn.commit()
	finally:
		if conn is not None:
					conn.close()
	return row