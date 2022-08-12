import numpy as np
cimport numpy as np

def _get_funcs_and_forces(x, trans, int atoms_num, weights, target_dists):

    cdef:
        list funcs=[], funcs_prime=[] 
       # np.ndarray[np.float, ndim=1] func, grad 

    for ni in range(len(x) - 2):
        vec = [x[ni + 1, i] - x[ni + 1] - trans[ni, i] for i in range(atoms_num)]

        trial_dist = np.linalg.norm(vec, axis=2)
        aux = (trial_dist - target_dists[ni]) * weights[ni] / (trial_dist + np.eye(atoms_num, dtype=np.float64))

        # Objective function
        func = np.sum((trial_dist - target_dists[ni]) ** 2 * weights[ni])

        # "True force" derived from the objective function.
        grad = np.sum(aux[:, :, None] * vec, axis=1)

        funcs.append(func)
        funcs_prime.append(grad)

    return funcs, funcs_prime