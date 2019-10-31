import matplotlib.pyplot as plt
import matplotlib
from density_db import density_database
import numpy as np

def main():
    delta_e = 50
    J = 50
    lambdaReorg = 50
    gamma = 50
    T = 300
    method = ['HEOM', 'Redfield', 'Forster'][1]

    db = density_database('test.db')
    fig, axs = plt.subplots(2, 2)
    for i in range(2):
        for j in range(2):
            index = i * 2 + j + 1
            c = db.selectDensity(delta_e, J, lambdaReorg, gamma, T, index, method)
            density = list(zip(*c.fetchall()))
            if density == []:
                continue
            axs[i, j].plot(density[0], density[1])
            axs[i, j].plot(density[0], density[2])
    plt.show()

if __name__ == '__main__':
    main()