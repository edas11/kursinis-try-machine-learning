from density_db import density_database
import numpy as np
from tqdm import tqdm
import math

class Error:

    def __init__(self, method):
        self.method = method
        self.db = density_database('density.db')

    def calculateErrorAndSave(self):
        propagations = self.db.selectMultiplePropagations(self.method).fetchall()
        for approxId, exactId in tqdm(propagations):
            error = self.calculateError(approxId, exactId)
            self.db.insertError(approxId, error)
            self.db.db.connection.commit()

    def calculateError(self, approxId, exactId):
        culmError = 0
        for i in range(2):
            for j in range(2):
                index = i * 2 + j + 1
                densityApprox = self.getDensity(approxId, index)
                densityExact = self.getDensity(exactId, index)
                equilibrationTime = int(self.getEquilibrationTime(densityExact))#get index, look at all i and j
                difference = densityApprox[equilibrationTime:, 1] + 1j * densityApprox[equilibrationTime:, 2] - densityExact[equilibrationTime:, 1] - 1j * densityExact[equilibrationTime:, 2]
                culmError += np.sum(np.square(np.absolute(difference)))
        return math.sqrt(culmError)/(4 * equilibrationTime)
    
    def getDensity(self, propagationId, index):
        c = self.db.selectDensityByPropagationId(propagationId, index)
        return np.array(c.fetchall())

    def getEquilibrationTime(self, density):
        last = density[-1, :]
        for row in density:
            deviation = np.absolute(row[1] + 1j * row[2] - last[1] - 1j * last[2])
            if deviation < 10**-3:
                return row[0]

if __name__ == '__main__':
    Error('Redfield').calculateErrorAndSave()