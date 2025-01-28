import random
import threading
import os

debug = False


def process_core_group(group, local_pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, group_id):
    if debug:
        print(f"[DEBUG] Start przetwarzania grupy {group_id + 1}. Proces ID: {os.getpid()}, Wątek: {threading.get_ident()}")

    local_updated_group = []

    for ant in group:
        for _ in ant.unvisited_cities:
            ant_cycle(ant, local_pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta)

        delta_pheromone = 1 / ant.total_cost
        local_pheromone_matrix = ant.update_pheromones(local_pheromone_matrix, rho, delta_pheromone)
        local_updated_group.append(ant)

    return local_updated_group, local_pheromone_matrix


def ant_cycle(ant, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta):
    probabilities = ant.calculate_probabilities(pheromone_matrix, visibility_matrix, alpha, beta)

    # next_city = random.choices(ant.unvisited_cities, probabilities)[0]
    next_city = choose_city(ant, probabilities)

    ant.visit_city(next_city, distance_matrix[ant.current_city][next_city])

    # if debug:
    #     print(f"probabilities: {probabilities}")


def choose_city(ant, probabilities):
    cumulative_probabilities = []
    cumulative_sum = 0
    for prob in probabilities:
        cumulative_sum += prob
        cumulative_probabilities.append(cumulative_sum)

    rand_value = random.random()

    next_city = ant.unvisited_cities[0]
    for i, cum_prob in enumerate(cumulative_probabilities):
        if rand_value < cum_prob:
            next_city = ant.unvisited_cities[i]
            break

    return next_city


def combine_pheromone_matrices(matrices):
    combined_matrix = sum(matrices) / len(matrices)
    return combined_matrix
