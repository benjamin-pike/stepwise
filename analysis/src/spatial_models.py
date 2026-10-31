import numpy as np
from scipy import sparse
from scipy.optimize import minimize_scalar
from spreg import ML_Error
from spreg.ml_error import err_c_loglik_sp


def se_coefficients(y, x, weights, epsilon = 1e-7, *, method = 'sparse'):
    y = np.asarray(y, dtype = float).reshape(-1, 1)

    if method == 'full':
        fitted = ML_Error(y, np.asarray(x, dtype = float), weights, method = 'full', epsilon = epsilon)

        return fitted.betas[:-1, 0], float(fitted.lam)

    if method != 'sparse':
        raise ValueError('method must be sparse or full')

    x = np.column_stack([np.ones(len(y)), np.asarray(x, dtype = float)])
    matrix = weights.sparse.tocsc()
    ylag, xlag = matrix @ y, matrix @ x
    
    optimum = minimize_scalar(
        err_c_loglik_sp,
        0.0,
        bounds = (-1.0, 1.0),
        args = (len(y), y, ylag, x, xlag, sparse.identity(len(y)), matrix),
        method = 'bounded',
        options = {'xatol': epsilon},
    )

    filtered_y = y - optimum.x * ylag
    filtered_x = x - optimum.x * xlag
    coefficients = np.linalg.inv(filtered_x.T @ filtered_x) @ (filtered_x.T @ filtered_y)

    return coefficients.ravel(), float(optimum.x)
