import numpy as np
from concurrent.futures import ProcessPoolExecutor
from src.common import process_core_group, combine_pheromone_matrices

debug = True


def process_ant_group(ant_group, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, num_cores):
    core_groups = np.array_split(ant_group, num_cores)

    updated_ant_group = []
    pheromone_matrices = []

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for i, group in enumerate(core_groups):
            futures.append(
                executor.submit(
                    process_core_group, group, np.copy(pheromone_matrix), visibility_matrix,
                    distance_matrix, alpha, beta, rho, i
                )
            )

        for future in futures:
            group_result, pheromone_matrix_result = future.result()
            updated_ant_group.extend(group_result)
            pheromone_matrices.append(pheromone_matrix_result)

    pheromone_matrix_result = combine_pheromone_matrices(pheromone_matrices)

    return updated_ant_group, pheromone_matrix_result


def run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, generations,
                   num_cores, num_pc):
    groups = np.array_split(ants, num_pc)

    for generation in range(generations):
        all_groups = []
        all_pheromone_matrices = []

        for i, group in enumerate(groups):
            group_result, pheromone_matrix_result = process_ant_group(np.copy(group), np.copy(pheromone_matrix),
                                                                      visibility_matrix, distance_matrix,
                                                                      alpha, beta, rho, num_cores)

            all_groups.append(group_result)
            all_pheromone_matrices.append(pheromone_matrix_result)

        pheromone_matrix = combine_pheromone_matrices(all_pheromone_matrices)

        for group in all_groups:
            for ant in group:
                ant.reset()

    return pheromone_matrix


def parallel_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                  generations, num_cores, num_pc):
    pheromone_matrix = run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                                      generations, num_cores, num_pc)

    return pheromone_matrix