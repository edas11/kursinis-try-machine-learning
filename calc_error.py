from density_db import density_database
import numpy as np

class Error:

    def __init__(self, method):
        self.method = method
        self.db = density_database('density.db')

    def calcError(self):
        propagations = self.db.selectMultiplePropagations(self.method).fetchall()
        for approxId, exactId in propagations:
            self.error(approxId, exactId)
            #self.db.selectDensityByPropagationId(propagation[''], 1)

    def error(self, approxId, exactId):
        culmError = 0
        for i in range(2):
            for j in range(2):
                index = i * 2 + j + 1
                c = self.db.selectDensityByPropagationId(approxId, index)
                densityApprox = np.array(c.fetchall())
                numOfPoints = len(densityApprox)
                c = self.db.selectDensityByPropagationId(exactId, index)
                densityExact =  np.array(c.fetchall())

                difference = densityApprox[:, 1] + 1j * densityApprox[:, 2] - densityExact[:, 1] - 1j * densityExact[:, 2]
                culmError += np.sum(np.square(np.absolute(difference)))
        print(numOfPoints)
        print(culmError/(4 * numOfPoints))
        exit()

if __name__ == '__main__':
    Error('Redfield').calcError()