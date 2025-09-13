import numpy as np
cimport numpy as cnp
cimport cython


@cython.boundscheck(False)
@cython.wraparound(False)
def _get_funcs_and_forces(cnp.ndarray[double, ndim=3] x, 
                          cnp.ndarray[double, ndim=4] trans, 
                          cnp.ndarray[double, ndim=3] weights, 
                          cnp.ndarray[double, ndim=3] target_dists):

    cdef:
        int images = x.shape[0] - 2;
        int atoms_num = x.shape[1];
        list funcs=[], funcs_prime=[]

        int ni=0;
        int i=0; 

    for ni from 0<=ni<images:
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
