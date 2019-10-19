import sys
import os
import pandas as pd
from config import config

rootDir = os.getcwd()

def do_work():
	args = sys.argv
	args = args[1:] # First element of args is the file name
    

if __name__ == '__main__':
	parameters = pd.read_csv("parameters.csv", sep = ",", index_col = False, dtype = 'float64')
	propagateCommandFormat = 'matlab -nodisplay -noFigureWindows -nosplash -nodesktop -wait -r "try; runHEOM(%f, %f, %f, %f, %f, 1, 1); catch E; quit(1); end; quit(0)"'

	errorRows = pd.DataFrame(columns=list(parameters.columns))
	os.chdir(config['methods']['HEOM']['rootDir'])
	for _, row in parameters.iterrows():
		propagateCommand = propagateCommandFormat % (row['delta_e'], row['J'], row['lambda'], row['gamma'], row['T'])
		result = os.system(propagateCommand)
		if result == 0:
			'todo write to db'
		else:
			errorRows = errorRows.append([row], ignore_index=True)

	os.chdir(rootDir)
	errorRows.to_csv('error.csv', index=False)