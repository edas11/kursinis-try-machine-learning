import pandas as pd
from db import create_connection, execute_sql
import time

select_params_sql = 'select params_id from propagation_parameters where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ?'
insert_params_sql = 'insert into propagation_parameters (delta_e, J, lambda, gamma, T) values(?, ?, ?, ?, ?)'
insert_density_sql = 'insert into density_dynamics values (?, ? ,? ,? ,?), (?, ? ,? ,? ,?), (?, ? ,? ,? ,?), (?, ? ,? ,? ,?)'

def main():
    start = time.time()
    
    delta_e = 100
    J = 100
    lambda_reorg = 100
    gamma = 100
    T = 300

    connection = create_connection()
    parameters = (delta_e, J, lambda_reorg, gamma, T)
    c = execute_sql(connection, select_params_sql, parameters)
    firstRow = c.fetchone()
    if firstRow == None:
        c = execute_sql(connection, insert_params_sql, parameters)
        params_id = c.lastrowid
    else:
        params_id = firstRow[0]

    data = pd.read_csv("heom_test.txt", sep = "\t", index_col = 't')
    for t, row in data.iterrows():
        if t%500 < 0.001:
            print(t)
        density_values =    (params_id, t, 1, row['Re(rho11)'], row['Im(rho11)'],
                            params_id, t, 2, row['Re(rho12)'], row['Im(rho12)'],
                            params_id, t, 4, row['Re(rho22)'], row['Im(rho22)'],
                            params_id, t, 3, row['Re(rho21)'], row['Im(rho21)'])
        c = execute_sql(connection, insert_density_sql, density_values)

    connection.commit()
    print(time.time() - start)

if __name__ == '__main__':
    
    main()