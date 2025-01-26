import random
debug = False


class Ant:
    def __init__(self, num_cities):
        self.start_city = random.randint(0, num_cities - 1)         # Miasto startowe
        self.current_city = self.start_city                            # Aktualne miasto
        self.unvisited_cities = list(range(num_cities))                # Zbiór nieodwiedzonych miast
        self.unvisited_cities.remove(self.start_city)
        self.path = [self.start_city]                                  # Tablica odwiedzonych miast (w kolejności)
        self.total_cost = 0                                            # Suma wag przebytej trasy
        self.num_cities = num_cities

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def visit_city(self, next_city, cost):
        self.unvisited_cities.remove(next_city)
        self.path.append(next_city)
        self.total_cost += cost
        self.current_city = next_city

    def has_visited(self, city):
        return city not in self.unvisited_cities

    def reset(self):
        self.current_city = self.start_city
        self.unvisited_cities = list(range(self.num_cities))
        self.unvisited_cities.remove(self.start_city)
        self.path = [self.start_city]
        self.total_cost = 0

    def calculate_probabilities(self, pheromone_matrix, visibility_matrix, alpha, beta):
        probabilities = []
        for city in self.unvisited_cities:
            tau = pheromone_matrix[self.current_city][city]
            eta = visibility_matrix[self.current_city][city]
            probabilities.append((tau ** alpha) * (eta ** beta))
        total = sum(probabilities)
        for i in range(len(probabilities)):
            probabilities[i] = probabilities[i] / total

        return probabilities

    def update_pheromones(self, pheromone_matrix, rho, delta_pheromone):
        for i in range(len(self.path) - 1):
            city_a = self.path[i]
            city_b = self.path[i + 1]
            pheromone_matrix[city_a][city_b] = (1 - rho) * pheromone_matrix[city_a][city_b] + delta_pheromone
            pheromone_matrix[city_b][city_a] = pheromone_matrix[city_a][city_b]

            if debug:
                print(f"pheromone_matrix[city_a][city_b]: {pheromone_matrix[city_a][city_b]}")

        return pheromone_matrix

    def __repr__(self):
        return f"Ant(start_city={self.start_city}, current_city={self.current_city}, total_cost={self.total_cost}, unvisited_cities={self.unvisited_cities}, path={self.path})"