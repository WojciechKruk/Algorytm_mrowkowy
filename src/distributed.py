import socket
import pickle
import numpy as np
from src.common import combine_pheromone_matrices

debug = True


def send_to_server(server_address, data):
    if debug:
        print(f"[DEBUG] Wysyłanie danych do serwera {server_address}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)
        s.connect(server_address)
        s.sendall(pickle.dumps(data))
        if debug:
            print("[DEBUG] Dane wysłane do serwera.")

        response = b""
        while True:
            if debug:
                print("[DEBUG] Oczekiwanie na dane od serwera...")
            part = s.recv(4096)
            if not part:
                print("[DEBUG] Odebrano koniec danych od serwera.")
                break
            if debug:
                print(f"[DEBUG] Odebrano część danych: {part}")
            response += part

        if debug:
            print("[DEBUG] Wszystkie dane odebrane, deserializacja odpowiedzi...")
        return pickle.loads(response)


def run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, generations,
                   num_cores, num_pc):
    servers = [("192.168.43.18", 8000), ("192.168.43.150", 8001)]
    groups = np.array_split(ants, num_pc)

    for generation in range(generations):
        print(f"[DEBUG] Generacja {generation + 1}/{generations}")

        all_groups = []
        all_pheromone_matrices = []

        for i, (group, server) in enumerate(zip(groups, servers)):
            print(f"[DEBUG] Wysyłanie grupy {i + 1}/{num_pc} do serwera {server}.")
            data_to_send = {
                "group": group,
                "pheromone_matrix": pheromone_matrix,
                "visibility_matrix": visibility_matrix,
                "distance_matrix": distance_matrix,
                "alpha": alpha,
                "beta": beta,
                "rho": rho,
                "num_cores": num_cores
            }
            result = send_to_server(server, data_to_send)
            print(f"Serwer {server} zwrócił wynik: {result}")

            all_groups.append(result["group_result"])
            all_pheromone_matrices.append(result["pheromone_matrix_result"])

        pheromone_matrix = combine_pheromone_matrices(all_pheromone_matrices)

        for group in all_groups:
            for ant in group:
                ant.reset()

    return pheromone_matrix


def distributed_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                     generations, num_cores, num_pc):
    pheromone_matrix = run_iterations(
        ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, generations, num_cores, num_pc
    )
    return pheromone_matrix
