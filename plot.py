import matplotlib.pyplot as plt
import matplotlib
from db import database
import numpy as np

select_density_sql = 'select time, real_density, imaginary_density from density_dynamics as dd inner join propagation as p on dd.propagation_id = p.propagation_id inner join propagation_parameters as pp on p.params_id = pp.params_id where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ? and density_index = ? and method = ?'

def main():
    delta_e = 50
    J = 50
    lambdaReorg = 50
    gamma = 50
    T = 200
    method = ['HEOM', 'Redfield', 'Forster'][2]

    db = database('density.db')
    fig, axs = plt.subplots(2, 2)
    for i in range(2):
        for j in range(2):
            index = i * 2 + j + 1
            c = db.execute_sql(select_density_sql, (delta_e, J, lambdaReorg, gamma, T, index, method))
            density = list(zip(*c.fetchall()))
            if density == []:
                continue
            axs[i, j].plot(density[0], density[1])
            axs[i, j].plot(density[0], density[2])
    plt.show()

if __name__ == '__main__':
    main()