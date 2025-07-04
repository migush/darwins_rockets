from darwins_rockets.rocket import Entity, Target, Rocket
from darwins_rockets.population import Population
import math
import numpy as np

class World:
    def __init__(self, width, height, population_size=50, dna_length=100, mutation_rate=0.1):
        """
        Initialize the World with genetic algorithm parameters.
        
        Args:
            width: World width in pixels
            height: World height in pixels  
            population_size: Number of rockets per generation
            dna_length: Number of thrust instructions per rocket
            mutation_rate: Probability of gene mutation (0.0 to 1.0)
        """
        # World dimensions and basic properties
        self.width = width
        self.height = height
        self.entities = []
        self.target = None
        
        # Genetic algorithm setup
        self.population_size = population_size
        self.dna_length = dna_length
        self.mutation_rate = mutation_rate
        
        # Create starting positions for rockets (e.g., bottom center)
        self.start_positions = [
            (int((i + 1) * width / (population_size + 1)), height - 50)
            for i in range(population_size)
        ]
        # Initialize population manager
        self.population = Population(
            start_positions=self.start_positions,
            dna_length=dna_length,
            mutation_rate=mutation_rate
        )
        
        # Generation tracking
        self.current_generation = 0
        self.generation_step = 0
        self.max_steps_per_generation = dna_length + 50  # Allow some extra time
        
        # Performance statistics
        self.stats = {
            'total_rockets_reached_target': 0,
            'best_distance_achieved': float('inf'),
            'rockets_reached_current_gen': 0,
            'best_fitness_current_gen': 0.0,
            'best_fitness_all_time': 0.0,
            'current_generation': 0,
            'generation_complete': False
        }
        
        # Initialize first generation
        self._spawn_generation()

    def add_entity(self, entity: Entity):
        """Add a non-rocket entity to the world (like targets)."""
        self.entities.append(entity)
        if isinstance(entity, Target):
            self.target = entity

    def remove_entity(self, entity: Entity):
        """Remove an entity from the world."""
        if entity in self.entities:
            self.entities.remove(entity)
            if entity is self.target:
                self.target = None

    def step(self):
        """
        Execute one simulation step. This is the main method called each frame.
        Handles both rocket updates and generation lifecycle management.
        """
        # Update all entities (rockets and targets)
        for entity in self.entities:
            entity.update(self)
        
        # Increment generation step counter
        self.generation_step += 1
        
        # Evaluate current generation performance
        self._calculate_rocket_stats()

        # Check if generation should end
        if self._should_end_generation():
            self._end_generation()
            self._spawn_generation()

    def _spawn_generation(self):
        """
        Create a new generation of rockets using DNA from the population.
        This happens at the start of each generation.
        """
        # Remove all existing rockets from entities
        self.entities = [e for e in self.entities if not isinstance(e, Rocket)]
        
        # Get DNA sequences from population
        dna_sequences = self.population.get_dnas()
        
        # Create new rockets with the DNA
        for i, (start_pos, dna) in enumerate(zip(self.start_positions, dna_sequences)):
            rocket = Rocket(start_pos, self.dna_length)
            # Replace the rocket's random DNA with evolved DNA
            rocket.dna = [np.array(gene, dtype=float) for gene in dna]
            rocket.current_step = 0  # Reset step counter
            self.entities.append(rocket)
        
        # Reset generation tracking
        self.generation_step = 0
        self.current_generation += 1
        self.stats['current_generation'] = self.current_generation
        self.stats['generation_complete'] = False
        
        print(f"Generation {self.current_generation} spawned with {len(self.get_rockets())} rockets")

    def _should_end_generation(self):
        """
        Determine if the current generation should end.
        
        Returns:
            bool: True if generation should end
        """
        rockets = self.get_rockets()
        
        # End if no rockets exist
        if not rockets:
            return True
            
        # End if maximum steps reached
        if self.generation_step >= self.max_steps_per_generation:
            return True
        
        # End if all rockets have either reached target or are out of fuel
        all_finished = True
        for rocket in rockets:
            # Rocket is still active if it has fuel and hasn't reached target
            if rocket.current_step < rocket.dna_length and not rocket.has_reached_target:
                all_finished = False
                break
        
        return all_finished

    def _end_generation(self):
        """
        Process the end of a generation. Evaluate all rockets and evolve population.
        """
        rockets = self.get_rockets()
        
        if not rockets:
            print(f"Generation {self.current_generation} ended with no rockets")
            return
        
        # Ensure all rockets have final fitness calculated
        if self.target:
            for rocket in rockets:
                rocket.evaluate_fitness(self.target.pos)
        
        # Update all-time best fitness
        for rocket in rockets:
            if rocket.fitness > self.stats['best_fitness_all_time']:
                self.stats['best_fitness_all_time'] = rocket.fitness
        
        # Evolve population based on rocket performance
        self.population.next_generation(rockets)
        
        # Mark generation as complete
        self.stats['generation_complete'] = True
        
        print(f"Generation {self.current_generation} complete:")
        print(f"  Rockets reached target: {self.stats['rockets_reached_current_gen']}")
        print(f"  Best fitness: {self.stats['best_fitness_current_gen']:.2f}")
        print(f"  Best distance: {self.stats['best_distance_achieved']:.2f}")

    def _calculate_rocket_stats(self):
        """
        Calculate and update statistics for the current generation.
        This runs every step to keep stats current.
        """
        rockets = [e for e in self.entities if isinstance(e, Rocket)]
        
        if not self.target or not rockets:
            return
        
        # Reset current generation stats
        best_dist = float('inf')
        rockets_reached = 0
        best_fitness = 0.0
        
        for rocket in rockets:
            # Ensure fitness is calculated
            rocket.evaluate_fitness(self.target.pos)
            
            # Calculate distance to target
            dist = math.hypot(
                rocket.pos[0] - self.target.pos[0], 
                rocket.pos[1] - self.target.pos[1]
            )
            
            # Update best distance
            if dist < best_dist:
                best_dist = dist
            
            # Count rockets that reached target
            if rocket.has_reached_target:
                rockets_reached += 1
            
            # Track best fitness
            if rocket.fitness > best_fitness:
                best_fitness = rocket.fitness
            
            # Apply out-of-bounds penalty
            if (rocket.pos[0] < 0 or rocket.pos[0] > self.width or 
                rocket.pos[1] < 0 or rocket.pos[1] > self.height):
                rocket.fitness *= 0.1
        
        # Update statistics
        self.stats['best_distance_achieved'] = best_dist
        self.stats['rockets_reached_current_gen'] = rockets_reached
        self.stats['best_fitness_current_gen'] = best_fitness
        
        # Update total rockets reached (cumulative across all generations)
        if rockets_reached > 0:
            self.stats['total_rockets_reached_target'] += rockets_reached

    def get_entities(self):
        """Get all entities in the world."""
        return list(self.entities)

    def get_rockets(self):
        """Get only the rocket entities."""
        return [e for e in self.entities if isinstance(e, Rocket)]

    def get_stats(self):
        """Get current performance statistics."""
        return self.stats.copy()

    def get_state(self):
        """Get the state of all entities for visualization."""
        return [entity.get_state() for entity in self.entities]

    def is_generation_complete(self):
        """Check if the current generation has finished."""
        return self.stats.get('generation_complete', False)

    def get_generation_progress(self):
        """
        Get the progress of the current generation as a percentage.
        
        Returns:
            float: Progress from 0.0 to 1.0
        """
        if self.max_steps_per_generation <= 0:
            return 1.0
        return min(1.0, self.generation_step / self.max_steps_per_generation)

    def set_target(self, x, y, radius=20):
        """
        Convenience method to set or update the target location.
        
        Args:
            x: Target x position
            y: Target y position  
            radius: Target radius (default 20)
        """
        # Remove existing target
        if self.target:
            self.remove_entity(self.target)
        
        # Add new target
        new_target = Target((x, y), radius)
        self.add_entity(new_target)

    @property
    def target_pos(self):
        if self.target is not None:
            return self.target.pos
        return (0, 0)
