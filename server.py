import numpy as np
from src.common import process_core_group, combine_pheromone_matrices
import socket
import pickle

debug = False


def process_ant_group(ant_group, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, num_cores):
    core_groups = np.array_split(ant_group, num_cores)

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


def handle_request(data):
    group = data["group"]
    pheromone_matrix = data["pheromone_matrix"]
    visibility_matrix = data["visibility_matrix"]
    distance_matrix = data["distance_matrix"]
    alpha = data["alpha"]
    beta = data["beta"]
    rho = data["rho"]
    num_cores = data["num_cores"]

    group_result, pheromone_matrix_result = process_ant_group(
        group, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, num_cores)

    return {"group_result": group_result, "pheromone_matrix_result": pheromone_matrix_result}


def start_server(host="localhost", port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Serwer uruchomiony na {host}:{port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Połączenie od: {addr}")
            with client_socket:
                data = client_socket.recv(4096)
                if not data:
                    break
                received_data = pickle.loads(data)
                result = handle_request(received_data)
                client_socket.sendall(pickle.dumps(result))


if __name__ == "__main__":
    start_server(host="localhost", port=8000)
