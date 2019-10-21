import sys
import os
import pandas as pd
from config import config
from db import create_connection, execute_sql
import time

class Runner:
	select_params_sql = 'select params_id from propagation_parameters where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ?'
	insert_params_sql = 'insert into propagation_parameters (delta_e, J, lambda, gamma, T) values(?, ?, ?, ?, ?)'
	insert_density_sql = 'insert into density_dynamics values (?, ?, ? ,? ,? ,?), (?, ?, ? ,? ,? ,?), (?, ?, ? ,? ,? ,?), (?, ?, ? ,? ,? ,?)'
	propagateCommandFormat = 'matlab -nodisplay -noFigureWindows -nosplash -nodesktop -wait -r "try; runHEOM(%f, %f, %f, %f, %f, 1, 1); catch E; quit(1); end; quit(0)"'
	propagationParameters = pd.read_csv("parameters.csv", sep = ",", index_col = False, dtype = 'float64')
	errorRows = pd.DataFrame(columns=list(propagationParameters.columns))
	rootDir = os.getcwd()

	def run(self):#todo log a little
		os.chdir(config['methods']['HEOM']['rootDir'])
		self.propagateForAllParameters()
		os.chdir(self.rootDir)
		self.errorRows.to_csv('error.csv', index=False)

	def propagateForAllParameters(self):
		for _, row in self.propagationParameters.iterrows():
			result = os.system(self.propagateCommandFormat % tuple(row))
			if result == 0:
				'todo write to db'
			else:
				self.errorRows = self.errorRows.append([row], ignore_index=True)

	def insertDataToDatabase(self):
		start = time.time()

		connection = create_connection()
		paramsId = self.insertParameters(connection)
		self.insertPropogationDataToDatabase(paramsId, connection)

		print(time.time() - start)

	def insertParameters(self, connection):
		delta_e = 100
		J = 100
		lambda_reorg = 100
		gamma = 100
		T = 300

		parameters = (delta_e, J, lambda_reorg, gamma, T)
		c = execute_sql(connection, self.select_params_sql, parameters)
		firstRow = c.fetchone()
		if firstRow == None:
			c = execute_sql(connection, self.insert_params_sql, parameters)
			params_id = c.lastrowid
		else:
			params_id = firstRow[0]
		return params_id

	def insertPropogationDataToDatabase(self, params_id, connection):
		data = pd.read_csv("heom_test.txt", sep = "\t", index_col = 't')
		for t, row in data.iterrows():
			if t%500 < 0.001:
				print(t)
			density_values =    (1, params_id, t, 1, row['Re(rho11)'], row['Im(rho11)'],
								1, params_id, t, 2, row['Re(rho12)'], row['Im(rho12)'],
								1, params_id, t, 4, row['Re(rho22)'], row['Im(rho22)'],
								1, params_id, t, 3, row['Re(rho21)'], row['Im(rho21)'])
			c = execute_sql(connection, self.insert_density_sql, density_values)
		connection.commit()

if __name__ == '__main__':
	Runner().insertDataToDatabase()