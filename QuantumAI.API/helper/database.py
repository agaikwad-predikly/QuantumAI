import sys
import psycopg2
from psycopg2.extras import NamedTupleCursor

def get_connection_string():
	return "host=quantum-ai-db.cqmxufpxd5v3.us-west-1.rds.amazonaws.com dbname=quantum_ai_db user=quantum_admin password=Quantum#456 connect_timeout=160"
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


def call_procedure_with_header(procedure_name, params):
	connection_string=get_connection_string()
	conn = psycopg2.connect(connection_string)
	results = []
	try:
		ncurs = conn.cursor(cursor_factory=NamedTupleCursor)
		ncurs.callproc(procedure_name,params)
		rows = ncurs.fetchall()
		colnames = [desc[0] for desc in ncurs.description]
		ncurs.close()
		conn.commit()
		for row in rows:
			results.append(dict(zip(colnames, row)))
	finally:
		if conn is not None:
					conn.close()
	return results

def vaccum(table):
	query = "VACUUM VERBOSE ANALYZE %s" % table
	connection_string=get_connection_string()
	conn = psycopg2.connect(connection_string)
	isolation_level = conn.isolation_level
	conn.set_isolation_level(0)
	cur = conn.cursor()
	cur.execute(query)
	# Set our isolation_level back to normal
	conn.set_isolation_level(isolation_level)
	return conn.notices
