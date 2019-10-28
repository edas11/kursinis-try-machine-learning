import sqlite3
from sqlite3 import Error
from db import database

# J - Rezonancine saveika (cm^-1)
# T - Temperatura (K)
# gamma - Relaksacijos laikas (fs)
# lambda - Reorganizacijos energija (cm^-1)
# delta_e - Site energiju skirtuma (cm^-1)

#todo metodas
sql_create_parameters_table = """
    CREATE TABLE IF NOT EXISTS propagation_parameters (
        params_id integer PRIMARY KEY AUTOINCREMENT ,
        delta_e real,
        J real,
        lambda real,
        gamma real,
        T real,
        UNIQUE(delta_e, J, lambda, gamma, T)
    );
"""

sql_create_propagation_table = """
    CREATE TABLE IF NOT EXISTS propagation (
        propagation_id integer PRIMARY KEY AUTOINCREMENT ,
        params_id integer,
        initial_cond_id integer,
        method text,
        FOREIGN KEY (params_id) REFERENCES propagation_parameters (params_id),
        UNIQUE(params_id, initial_cond_id, method)
    );
"""
 
sql_create_density_table = """
    CREATE TABLE IF NOT EXISTS density_dynamics (
        propagation_id integer,
        time real,
        density_index integer,
        real_density real,
        imaginary_density real,
        FOREIGN KEY (propagation_id) REFERENCES density_dynamics (propagation_id),
        PRIMARY KEY (propagation_id, time, density_index)
    );
"""

def main():
    db = database('density.db')
    db.execute_sql(sql_create_parameters_table)
    db.execute_sql(sql_create_propagation_table)
    db.execute_sql(sql_create_density_table)
 
if __name__ == '__main__':
    main()