import sys
import os
import pandas as pd
from config import config
from db import database
import time
import itertools

class Runner:
	select_params_sql = 'select params_id from propagation_parameters where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ?'
	insert_params_sql = 'insert into propagation_parameters (delta_e, J, lambda, gamma, T) values(?, ?, ?, ?, ?)'
	insert_propagation_sql = 'insert into propagation (params_id, initial_cond_id, method) values(?, ?, ?)'
	insert_density_sql = 'insert into density_dynamics values (?, ?, ? ,? ,?), (?, ? ,? ,? ,?), (?, ? ,? ,? ,?), (?, ? ,? ,? ,?)'
	propagateCommandFormat = 'matlab -nodisplay -noFigureWindows -nosplash -nodesktop -wait -r "try; runHEOM(%f, %f, %f, %f, %f, 1, 1); catch E; quit(1); end; quit(0)"'
	rootDir = os.getcwd()
	db = database('density.db')

	def __init__(self):
		#self.propagationParameters = pd.read_csv("parameters.csv", sep = ",", index_col = False, dtype = 'float64')
		self.propagationParameters = pd.DataFrame(self.get_parameters())
		self.errorRows = pd.DataFrame(columns=['delta_e', 'J', 'lambda', 'gamma', 'T'])

	def run(self):
		os.chdir(config['methods']['HEOM']['rootDir'])
		self.propagateForAllParameters()
		os.chdir(self.rootDir)
		self.errorRows.to_csv('error.csv', index=False)

	def propagateForAllParameters(self):
		for i, row in self.propagationParameters.iterrows():
			print('%i. Starting %s' % (i, tuple(row)))
			start = time.time()
			result = os.system(self.propagateCommandFormat % tuple(row))
			if result == 0:
				print('Propagation success, elapsed %f, starting insert to db' % (time.time() - start))
				self.insertDataToDatabase(tuple(row))
				os.remove('density.txt')
			else:
				print('Propagation error')
				self.errorRows = self.errorRows.append([row], ignore_index=True)
			print('Finished, elaplsed %f' % (time.time() - start))
				

	def insertDataToDatabase(self, parameters):
		paramsId = self.insertParameters(parameters)
		propagationId = self.insetPropagationEntry(paramsId)
		self.db.connection.commit()
		self.insertPropagationDataToDatabase(propagationId)

	def insertParameters(self, parameters):
		c = self.db.execute_sql(self.select_params_sql, parameters)
		firstRow = c.fetchone()
		if firstRow == None:
			c = self.db.execute_sql(self.insert_params_sql, parameters)
			params_id = c.lastrowid
		else:
			params_id = firstRow[0]
		return params_id

	def insetPropagationEntry(self, paramsId):
		c = self.db.execute_sql(self.insert_propagation_sql, (paramsId, 1, 'HEOM'))
		return c.lastrowid

	def insertPropagationDataToDatabase(self, propagationId):
		data = pd.read_csv("density.txt", sep = "\t", index_col = 't')
		for t, row in data.iterrows():
			density_values =    (propagationId, t, 1, row['Re(rho11)'], row['Im(rho11)'],
								propagationId, t, 2, row['Re(rho12)'], row['Im(rho12)'],
								propagationId, t, 4, row['Re(rho22)'], row['Im(rho22)'],
								propagationId, t, 3, row['Re(rho21)'], row['Im(rho21)'])
			self.db.execute_sql(self.insert_density_sql, density_values)
		self.db.connection.commit()

	def get_parameters(self):
		params = [
			[100, 200, 300, 400, 500],#delta_d
			[100, 300],#J
			[100, 200],#lambdaReorg
			[100],#gamma
			[200, 300]#T
		]
		return itertools.product(*params)

if __name__ == '__main__':
	Runner().run()