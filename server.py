import socket
import pickle
from src.parallel import process_ant_group

debug = False


def handle_request(data):
    if debug:
        print("[DEBUG] Rozpoczęcie przetwarzania żądania...")

    group = data["group"]
    pheromone_matrix = data["pheromone_matrix"]
    visibility_matrix = data["visibility_matrix"]
    distance_matrix = data["distance_matrix"]
    alpha = data["alpha"]
    beta = data["beta"]
    rho = data["rho"]
    num_cores = data["num_cores"]

    if debug:
        print(f"[DEBUG] num_cores: {num_cores}")

    group_result, pheromone_matrix_result = process_ant_group(
        group, pheromone_matrix, visibility_matrix, distance_matrix, alpha, beta, rho, num_cores)

    if debug:
        print(f"[DEBUG] Przetwarzanie zakończone.")

    return {"group_result": group_result, "pheromone_matrix_result": pheromone_matrix_result}


def start_server(host="192.168.43.18", port=8000):
    if debug:
        print("[DEBUG] Uruchamianie serwera...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        if debug:
            print(f"Serwer uruchomiony na {host}:{port}")

        while True:
            client_socket, addr = server_socket.accept()
            if debug:
                print(f"Połączenie od: {addr}")
            with client_socket:
                try:
                    client_socket.settimeout(120)
                    data = b""
                    while True:
                        part = client_socket.recv(8192)
                        if not part:
                            break
                        data += part

                    if not data:
                        print("[ERROR] Otrzymano pusty pakiet.")
                        continue

                    if debug:
                        print(f"[DEBUG] Odebrano dane od klienta.")

                    received_data = pickle.loads(data)
                    result = handle_request(received_data)

                    if debug:
                        print(f"[DEBUG] Wysyłanie odpowiedzi do klienta...")
                    client_socket.sendall(pickle.dumps(result))

                    if debug:
                        print("[DEBUG] Odpowiedź wysłana.")

                except socket.timeout:
                    print("[SERWER] Odbieranie danych zakończone z powodu przekroczenia czasu.")
                except Exception as e:
                    print(f"[ERROR] Błąd podczas obsługi połączenia: {e}")


if __name__ == "__main__":
    start_server(host="192.168.43.18", port=8000)
