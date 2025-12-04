import random
from typing import Tuple, Sequence
import numpy as np
from ga_models.ga_protocol import GAModel
from ga_models.activation import tanh, softmax

# GA = Genetic Algorithm
class SimpleModel(GAModel):
    def __init__(self, *, dims: Tuple[int, ...]):
        assert len(dims) >= 2, 'Error: dims must be two or higher.'
        self.dims = dims
        self.DNA = []
        for i, dim in enumerate(dims):
            if i < len(dims) - 1:
                # Initialize weights (TODO THIS IS UPDATED - WHY)
                self.DNA.append(np.random.rand(dim, dims[i+1]) * 2 - 1)

    def update(self, obs: Sequence) -> Tuple[int, ...]:
        x = obs
        for i, layer in enumerate(self.DNA):
            if not i == 0:
                x = tanh(x)
            x = x @ layer
        return softmax(x) # returns all output options with a total of 1.0 
        # (4 in the snake game - each direction)
        # For ours probably 10 or 9 (options for the next destination)

    def action(self, obs: Sequence):
        return self.update(obs).argmax() # chooses the output with most probability
    
    def get_tour(self, obs: Sequence) -> list:
        """
        Translates NN output into a TSP Path.
        1. Get scores for all cities.
        2. Sort indices based on scores (highest score = visit first).
        """
        scores = self.update(obs)
        # argsort returns indices that would sort the array; 
        # [::-1] reverses it so highest probability is first.
        tour_indices = np.argsort(scores)[::-1]
        return tour_indices.tolist()

    def mutate(self, mutation_rate=0.01) -> None:
        if random.random() < mutation_rate:
            random_layer = random.randint(0, len(self.DNA) - 1)
            row = random.randint(0, self.DNA[random_layer].shape[0] - 1)
            col = random.randint(0, self.DNA[random_layer].shape[1] - 1)
            self.DNA[random_layer][row][col] = random.uniform(-0.1, 0.1) # Small nudge - TODO why

    def __add__(self, other):
        # We are creating a new "Brain" (Neural Network)
        baby = SimpleModel(dims=self.dims)
        baby.DNA = []

        # 'mom_layer' and 'dad_layer' are NOT lists of cities (e.g., [0, 5, 2]).
        # They are matrices of numbers (weights) that decide HOW to think.
        for mom_layer, dad_layer in zip(self.DNA, other.DNA):
            
            # We are swapping pieces of "intelligence," not pieces of the map.
            # It is impossible to "double visit" a city here because 
            # there are no city IDs in these variables.
            if random.random() > 0.5:
                baby.DNA.append(mom_layer.copy())
            else:
                baby.DNA.append(dad_layer.copy())
                
        return baby

    def DNA(self):
        return self.DNA
