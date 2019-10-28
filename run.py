import sys
import os
import pandas as pd
from config import config
from db import database
import time
import itertools
import datetime

class Runner:
	select_params_sql = 'select params_id from propagation_parameters where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ?'
	insert_params_sql = 'insert into propagation_parameters (delta_e, J, lambda, gamma, T) values(?, ?, ?, ?, ?)'
	insert_propagation_sql = 'insert into propagation (params_id, initial_cond_id, method) values(?, ?, ?)'
	insert_density_sql = 'insert into density_dynamics values (?, ?, ? ,? ,?), (?, ? ,? ,? ,?), (?, ? ,? ,? ,?), (?, ? ,? ,? ,?)'
	rootDir = os.getcwd()
	db = database('density.db')

	def __init__(self, method):
		#self.propagationParameters = pd.read_csv("parameters.csv", sep = ",", index_col = False, dtype = 'float64')
		self.method = method
		self.propagationParameters = pd.DataFrame(self.get_parameters())
		self.errorRows = pd.DataFrame(columns=['delta_e', 'J', 'lambda', 'gamma', 'T'])

	def run(self):
		os.chdir(config['methods'][self.method]['rootDir'])
		self.propagateForAllParameters()
		os.chdir(self.rootDir)
		self.errorRows.to_csv('error_%s.csv' % time.time(), index=False)

	def propagateForAllParameters(self):
		for i, row in self.propagationParameters.iterrows():
			print('[%s] %i. Starting %s' % (datetime.datetime.now(), i, tuple(row)))
			self.start = time.time()
			paramsId, isNewEntry = self.insertParameters(tuple(row))
			if isNewEntry:
				self.propagate(tuple(row), paramsId)
			else:
				print('Parameters already in database, skipping.')
			print('Finished, elaplsed %f' % (time.time() - self.start))
				
	def propagate(self, parametersRow, paramsId):
		result = os.system(config['methods'][self.method]['command'] % tuple(parametersRow))
		if result == 0:
			print('Propagation success, elapsed %f, starting insert to db' % (time.time() - self.start))
			self.insertDataToDatabase(paramsId)
			os.remove('density.txt')
		else:
			print('Propagation error')
			self.errorRows = self.errorRows.append([parametersRow], ignore_index=True)

	def insertDataToDatabase(self, paramsId):
		propagationId = self.insertPropagationEntry(paramsId)
		self.db.connection.commit()
		self.insertPropagationDataToDatabase(propagationId)

	def insertParameters(self, parameters):
		c = self.db.execute_sql(self.select_params_sql, parameters)
		firstRow = c.fetchone()
		if firstRow == None:
			c = self.db.execute_sql(self.insert_params_sql, parameters)
			params_id = c.lastrowid
			isNewEntry = True
		else:
			params_id = firstRow[0]
			isNewEntry = False
		return (params_id, isNewEntry)

	def insertPropagationEntry(self, paramsId):
		c = self.db.execute_sql(self.insert_propagation_sql, (paramsId, 1, self.method))
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
			[50, 100, 200, 400],#delta_d
			[50, 100, 200, 400],#J
			[50, 100, 200, 400],#lambdaReorg
			[50, 100, 200, 300],#gamma
			[200, 300]#T
		]
		return itertools.product(*params)

if __name__ == '__main__':
	methods = ('HEOM', 'Redfield', 'Forster')
	methodNr = int(input('Choose method:\n1. %s\n2. %s\n3. %s\n' % methods))
	Runner(methods[methodNr - 1]).run()