import numpy as np
from src.common import process_core_group, combine_pheromone_matrices

debug = False


def run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, generations,
                   num_cores, num_pc):
    # Podział mrówek na grupy
    groups = np.array_split(ants, num_pc)

    for generation in range(generations):
        if debug:
            print(f"Generacja {generation + 1}/{generations}")

        all_groups = []
        all_pheromone_matrices = []

        for i, group in enumerate(groups):
            group_result, pheromone_matrix_result = process_ant_group(np.copy(group), np.copy(pheromone_matrix),
                                                                      visibility_matrix, distance_matrix,
                                                                      alpha, beta, rho, num_cores)

            all_groups.append(group_result)
            all_pheromone_matrices.append(pheromone_matrix_result)

        pheromone_matrix = combine_pheromone_matrices(all_pheromone_matrices)

        if debug:
            print(f"Ants: {ants}")
            # print(f"Pheromone matrix group 1: {pheromone_matrix_group1}")
            # print(f"Pheromone matrix group 2: {pheromone_matrix_group2}")
            print(f"Pheromone matrix: \n{pheromone_matrix}")

        for group in all_groups:
            for ant in group:
                ant.reset()

    return pheromone_matrix


def process_ant_group(ant_group, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, num_cores):
    core_groups = np.array_split(ant_group, num_cores)
    if debug:
        print(f"core groups: {core_groups}")

    futures = []
    updated_ant_group = []
    pheromone_matrices = []

    for i, group in enumerate(core_groups):
        futures.append(
            process_core_group(group, np.copy(pheromone_matrix), visibility_matrix, distance_matrix, alpha, beta,
                               rho, i)
        )

    for group_result, pheromone_matrix_result in futures:
        updated_ant_group.extend(group_result)
        pheromone_matrices.append(pheromone_matrix_result)

    pheromone_matrix_result = combine_pheromone_matrices(pheromone_matrices)

    return ant_group, pheromone_matrix_result


def sequential_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                    generations, num_cores, num_pc):
    pheromone_matrix = run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                                      generations, num_cores, num_pc)

    return pheromone_matrix
