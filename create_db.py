import sqlite3
from sqlite3 import Error
from db import create_connection, execute_sql

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
 
sql_create_density_table = """
    CREATE TABLE IF NOT EXISTS density_dynamics (
        params_id integer,
        time real,
        density_index integer,
        real_density real,
        imaginary_density real,
        FOREIGN KEY (params_id) REFERENCES propagation_parameters (params_id),
        PRIMARY KEY (params_id, time, density_index)
    );
"""

def main():
    connection = create_connection()
    execute_sql(connection, sql_create_parameters_table)
    execute_sql(connection, sql_create_density_table)
 
if __name__ == '__main__':
    main()