from multiprocessing import Pool, current_process

def worker_function(data):
    print(f"Proces ID: {current_process().pid}, Przetwarzam: {data}")
    return data * 2

if __name__ == "__main__":
    data = [1, 2, 3, 4, 5]
    with Pool(2) as pool:
        results = pool.map(worker_function, data)
    print("Wyniki:", results)
