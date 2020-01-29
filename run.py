import sys
import os
import pandas as pd
from config import config
from density_db import density_database
import time
import itertools
import datetime

class Runner:

	def __init__(self, method):
		#self.propagationParameters = pd.read_csv("parameters.csv", sep = ",", index_col = False, dtype = 'float64')
		self.method = method
		self.propagationParameters = pd.DataFrame(self.get_parameters())
		self.errorRows = pd.DataFrame(columns=['delta_e', 'J', 'lambda', 'gamma', 'T'])
		self.db = density_database('density.db')
		self.rootDir = os.getcwd()

	def run(self):
		os.chdir(config['methods'][self.method]['rootDir'])
		self.propagateForAllParameters()
		os.chdir(self.rootDir)
		self.errorRows.to_csv('error_%s_%s.csv' % (self.method, time.time()), index=False)

	def propagateForAllParameters(self):
		for i, row in self.propagationParameters.iterrows():
			print('[%s] %i. Starting %s, %s' % (datetime.datetime.now(), i, tuple(row), self.method))
			self.start = time.time()
			paramsId = self.insertParameters(tuple(row))
			if self.hasNotBeenPropagated(paramsId):
				self.propagate(row, paramsId)
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
	
	def hasNotBeenPropagated(self, paramsId):
		firstRow = self.db.selectPropagation(paramsId, self.method).fetchone()
		if firstRow == None:
			return True
		else:
			return False

	def insertDataToDatabase(self, paramsId):
		propagationId = self.db.insertPropagationEntry(paramsId, self.method)
		self.db.db.connection.commit()
		self.insertPropagationDataToDatabase(propagationId)

	def insertParameters(self, parameters):
		firstRow = self.db.selectParameters(parameters).fetchone()
		if firstRow == None:
			params_id = self.db.insertParameters(parameters)
		else:
			params_id = firstRow[0]
		return params_id

	def insertPropagationDataToDatabase(self, propagationId):
		data = pd.read_csv("density.txt", sep = "\t", index_col = 't')
		for t, row in data.iterrows():
			if self.method == 'Forster':
				density_values = [(propagationId, t, 1, row['rho11'], 0),
									(propagationId, t, 4, row['rho22'],0)]
			else:
				density_values =    [(propagationId, t, 1, row['Re(rho11)'], row['Im(rho11)']),
									(propagationId, t, 2, row['Re(rho12)'], row['Im(rho12)']),
									(propagationId, t, 4, row['Re(rho22)'], row['Im(rho22)']),
									(propagationId, t, 3, row['Re(rho21)'], row['Im(rho21)'])]
			self.db.insertDensity(density_values)
		self.db.db.connection.commit()

	def get_parameters(self):
		params = [
			[50, 100, 200, 400],#delta_d
			[50, 100, 200, 400],#J
			[10, 25, 50, 100, 200, 400],#lambdaReorg
			[10, 25, 50, 100, 200, 300],#gamma
			[200, 300]#T
		]
		return itertools.product(*params)

if __name__ == '__main__':
	methods = ('HEOM', 'Redfield', 'Forster')
	#methodNr = int(input('Choose method:\n1. %s\n2. %s\n3. %s\n' % methods))
	methodNr = int(sys.argv[1])
	Runner(methods[methodNr]).run()