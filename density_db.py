from db import database

select_params_sql = 'select params_id from propagation_parameters where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ?'
select_propagation_sql = 'select propagation_id from propagation where params_id = ? and method = ?'
insert_params_sql = 'insert into propagation_parameters (delta_e, J, lambda, gamma, T) values(?, ?, ?, ?, ?)'
insert_propagation_sql = 'insert into propagation (params_id, initial_cond_id, method) values(?, ?, ?)'
insert_density_sql = 'insert into density_dynamics values (?, ?, ? ,? ,?)'
select_density_sql = 'select time, real_density, imaginary_density from density_dynamics as dd inner join propagation as p on dd.propagation_id = p.propagation_id inner join propagation_parameters as pp on p.params_id = pp.params_id where delta_e = ? and J = ? and lambda = ? and gamma = ? and T = ? and density_index = ? and method = ?'
select_density_by_propagation_id_sql = 'select time, real_density, imaginary_density from density_dynamics where propagation_id = ? and density_index = ?'
select_multiple_propagations_sql = 'select p_approx.propagation_id, p_heom.propagation_id from propagation as p_approx inner join propagation as p_heom on p_approx.params_id = p_heom.params_id and p_approx.initial_cond_id = p_heom.initial_cond_id where p_approx.method = ? and p_heom.method = "HEOM" and p_approx.propagation_id not in (select propagation_id from errors)'
insert_error_sql = 'insert into errors values (?, ?)'
select_errors_for_param_sql = 'select error, PARAM0 from errors as e inner join propagation as p on e.propagation_id = p.propagation_id inner join propagation_parameters as param on param.params_id = p.params_id where PARAM1 = ? and PARAM2 = ? and PARAM3 = ? and PARAM4 = ?'

class density_database:

    def __init__(self, db_file = 'test.db'):
        self.db = database(db_file)

    def selectPropagation(self, paramsId, method):
        return self.db.execute_sql(select_propagation_sql, (paramsId, method))

    def insertPropagationEntry(self, paramsId, method):
        c = self.db.execute_sql(insert_propagation_sql, (paramsId, 1, method))
        return c.lastrowid

    def selectMultiplePropagations(self, method):
        return self.db.execute_sql(select_multiple_propagations_sql, (method,))

    def selectParameters(self, parameters):
        return self.db.execute_sql(select_params_sql, parameters)

    def insertParameters(self, parameters):
        c = self.db.execute_sql(insert_params_sql, parameters)
        return c.lastrowid

    def selectDensity(self, delta_e, J, lambdaReorg, gamma, T, index, method):
        return self.db.execute_sql(select_density_sql, (delta_e, J, lambdaReorg, gamma, T, index, method))

    def selectDensityByPropagationId(self, propagationId, densityIndex):
        return self.db.execute_sql(select_density_by_propagation_id_sql, (propagationId, densityIndex))

    def insertDensity(self, density_values):
        c = self.db.execute_sql(insert_density_sql, density_values)
        return c.lastrowid

    def insertError(self, propagationId, error):
        c = self.db.execute_sql(insert_error_sql, (propagationId, error))
        return c.lastrowid

    def selectErrorsForParam(self, paramNames, params):
        sql = select_errors_for_param_sql
        sql = sql.replace('PARAM0', paramNames[0], 1)
        sql = sql.replace('PARAM1', paramNames[1], 1)
        sql = sql.replace('PARAM2', paramNames[2], 1)
        sql = sql.replace('PARAM3', paramNames[3], 1)
        sql = sql.replace('PARAM4', paramNames[4], 1)
        return self.db.execute_sql(sql, params)
