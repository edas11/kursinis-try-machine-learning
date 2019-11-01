import matplotlib.pyplot as plt
import matplotlib
from density_db import density_database

def main():
    paramNames = ('J', 'delta_e', 'lambda', 'gamma', 'T')
    params = (100, 100, 100, 300)
    db = density_database('density.db')
    c = db.selectErrorsForParam(paramNames, params)
    errors = list(zip(*c.fetchall()))
    print(errors)
    plt.plot(errors[1], errors[0])
    plt.yscale('log')
    plt.show()

if __name__ == '__main__':
    main()