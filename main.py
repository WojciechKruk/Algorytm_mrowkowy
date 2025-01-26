import numpy as np
import matplotlib.pyplot as plt
from Ant import Ant
from src.sequential import sequential_main
from src.parallel import parallel_main
from src.distributed import distributed_main
import matplotlib

matplotlib.use('TkAgg')
debug = False


def calculate_distance_matrix(file_path):
    coordinates = np.loadtxt(file_path, delimiter=',')

    num_cities = coordinates.shape[0]

    distance_matrix = np.zeros((num_cities, num_cities))

    for i in range(num_cities):
        for j in range(num_cities):
            if i != j:
                distance_matrix[i][j] = np.linalg.norm(coordinates[i] - coordinates[j])

    return distance_matrix, num_cities


def initialize_ants(num_cities, num_ants):
    ants = [Ant(num_cities) for _ in range(num_ants)]
    return ants


def find_best_path(pheromone_matrix, distance_matrix, num_cities):
    visited = set()
    current_city = 0
    next_city = None
    path = [current_city]
    total_cost = 0

    while len(visited) < num_cities - 1:
        visited.add(current_city)
        max_pheromone = -1

        for city in range(num_cities):
            if city not in visited and pheromone_matrix[current_city][city] > max_pheromone:
                max_pheromone = pheromone_matrix[current_city][city]
                next_city = city

        total_cost += distance_matrix[current_city][next_city]
        path.append(next_city)
        current_city = next_city

    total_cost += distance_matrix[current_city][path[0]]
    path.append(path[0])

    return path, total_cost


def plot_path(file_path, final_path):
    coordinates = np.loadtxt(file_path, delimiter=',')

    x_coords = coordinates[:, 0]
    y_coords = coordinates[:, 1]

    plt.scatter(x_coords, y_coords, c='red', label='Miasta', zorder=2)
    plt.scatter(x_coords[0], y_coords[0], c='green', label='Miasta', zorder=2)

    for i, (x, y) in enumerate(coordinates):
        plt.text(x, y, str(i), fontsize=12, ha='right', color='blue', zorder=3)

    ordered_coords = coordinates[final_path]
    plt.plot(ordered_coords[:, 0], ordered_coords[:, 1], c='black', linestyle='-', linewidth=1, zorder=1)

    plt.title("Najlepsza trasa")
    plt.show()


def main():
    file_path = r"C:\Users\krukw\PycharmProjects\Algorytm_mrowkowy\data\tiny.csv"
    num_ants = 10  # Liczba mrówek
    generations = 100  # Graniczna liczba generacji
    alpha = 1.0  # Waga wpływu feromonów
    beta = 2.0  # Waga wpływu widoczności
    rho = 0.1  # Współczynnik parowania feromonów
    num_cores = 1  # Liczba procesorów
    num_pc = 1  # Liczba rozproszenia
    mode = 3  # Tryb algorytmu 1-Sekwencyjny 2-równoległy 3-rozproszony

    # macierz odległości między miastami
    distance_matrix, num_cities = calculate_distance_matrix(file_path)

    # macierz feromonów
    pheromone_matrix = np.ones((num_cities, num_cities))

    # Macierz widoczności (odwrotności odległości)
    visibility_matrix = 1 / np.where(distance_matrix > 0, distance_matrix, np.inf)

    # Inicjalizacja mrówek
    ants = initialize_ants(num_cities, num_ants)

    # Algorytm
    if mode == 1:
        pheromone_matrix = sequential_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                                           generations, num_cores, num_pc)
    elif mode == 2:
        pheromone_matrix = parallel_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                                         generations, num_cores, num_pc)
    elif mode == 3:
        pheromone_matrix = distributed_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta,
                                            rho, generations, num_cores, num_pc)

    if debug:
        print(f"\nostateczna macierz feromonów: \n{pheromone_matrix}")

    # znajdowanie najlepszej ścieżki
    final_path, total_cost = find_best_path(pheromone_matrix, distance_matrix, num_cities)

    if debug:
        print(f"\nostateczna ścieżka: {final_path}")
        print(f"\ncałkowity koszt: {total_cost}")
        plot_path(file_path, final_path)


if __name__ == "__main__":
    from multiprocessing import set_start_method

    set_start_method("spawn", force=True)

    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.dump_stats("profiling_results.prof")  # Wyświetl: snakeviz profiling_results.prof
    stats.print_stats(20)
