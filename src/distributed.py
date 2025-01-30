import socket
import pickle
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from src.common import combine_pheromone_matrices
# import zlib

debug = False


def send_to_server(server_address, data):
    if debug:
        print(f"[DEBUG] Wysyłanie danych do serwera {server_address}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(120)
        s.connect(server_address)
        s.sendall(pickle.dumps(data))
        if debug:
            print("[DEBUG] Dane wysłane do serwera.")

        s.shutdown(socket.SHUT_WR)

        response = b""
        while True:
            part = s.recv(8192)
            if not part:
                if debug:
                    print("[DEBUG] Odebrano koniec danych od serwera.")
                break
            response += part

        if debug:
            print("[DEBUG] Wszystkie dane odebrane, deserializacja odpowiedzi...")
        return pickle.loads(response)


def run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, generations,
                   num_cores, num_pc):
    servers = [("192.168.43.18", 8000), ("192.168.43.150", 8001)]
    server_cores = {"192.168.43.18": 6, "192.168.43.150": 4}

    if num_pc == 2:
        # groups = np.split(ants, [int(len(ants) * server_cores["192.168.43.18"] / sum(server_cores.values()))])
        groups = np.split(ants, [int(len(ants) * 0.8)])
    else:
        groups = np.array_split(ants, num_pc)

    if debug:
        if num_pc == 1:
            print(f"group size of group 1: {len(groups[0])}")
        elif num_pc == 2:
            print(f"group size of group 1: {len(groups[0])}")
            print(f"group size of group 2: {len(groups[1])}")

    for generation in range(generations):
        if debug:
            print(f"[DEBUG] Generacja {generation + 1}/{generations}")

        all_groups = []
        all_pheromone_matrices = []

        with ProcessPoolExecutor(max_workers=num_pc) as executor:
            futures = [
                executor.submit(
                    send_to_server,
                    server,
                    {
                        "group": group,
                        "pheromone_matrix": pheromone_matrix,
                        "visibility_matrix": visibility_matrix,
                        "distance_matrix": distance_matrix,
                        "alpha": alpha,
                        "beta": beta,
                        "rho": rho,
                        "num_cores": server_cores.get(server[0], num_cores)
                    }
                )
                for server, group in zip(servers, groups)
            ]

            for future in futures:
                result = future.result()
                all_groups.append(result["group_result"])
                all_pheromone_matrices.append(result["pheromone_matrix_result"])

        pheromone_matrix = combine_pheromone_matrices(all_pheromone_matrices)

        for group in all_groups:
            for ant in group:
                ant.reset()

    return pheromone_matrix


def distributed_main(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                     generations, num_cores, num_pc):
    pheromone_matrix = run_iterations(ants, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho,
                                      generations, num_cores, num_pc)
    return pheromone_matrix
