import math
import random
from typing import List, Dict, Any, Tuple
import numpy as np
from dataclasses import dataclass
from abc import ABC, abstractmethod

class Entity(ABC):
    @abstractmethod
    def update(self, world):
        pass
    @abstractmethod
    def get_state(self):
        pass

@dataclass
class RocketConfig:
    """Configuration constants for rocket behavior."""
    DEFAULT_DNA_LENGTH: int = 100
    RADIUS: float = 5.0
    MAX_TRAIL_LENGTH: int = 50
    VELOCITY_DAMPING: float = 0.98  # 2% velocity loss per frame
    MAX_VELOCITY: float = 10.0
    MIN_THRUST_MAGNITUDE: float = 0.1
    MAX_THRUST_MAGNITUDE: float = 0.5
    TARGET_RADIUS: float = 20.0
    FITNESS_TARGET_REWARD: float = 1000.0
    FITNESS_BONUS_PER_STEP: float = 10.0


class Vector2D:
    """Utility class for 2D vector operations."""
    
    @staticmethod
    def random_unit_vector() -> np.ndarray:
        """Generate a random unit vector (magnitude = 1)."""
        angle = random.uniform(0, 2 * math.pi)
        return np.array([math.cos(angle), math.sin(angle)], dtype=float)
    
    @staticmethod
    def random_thrust_vector(min_magnitude: float, max_magnitude: float) -> np.ndarray:
        """Generate a random thrust vector with specified magnitude range."""
        direction = Vector2D.random_unit_vector()
        magnitude = random.uniform(min_magnitude, max_magnitude)
        return direction * magnitude
    
    @staticmethod
    def limit_magnitude(vector: np.ndarray, max_magnitude: float) -> np.ndarray:
        """Limit a vector's magnitude to the specified maximum."""
        magnitude = np.linalg.norm(vector)
        if magnitude > max_magnitude:
            return vector / magnitude * max_magnitude
        return vector
    
    @staticmethod
    def safe_distance(pos1: np.ndarray, pos2: np.ndarray) -> float:
        """Calculate distance between two positions, handling edge cases."""
        return np.linalg.norm(pos1 - pos2)


class Rocket(Entity):
    """
    A rocket entity that navigates using genetic algorithm DNA.
    
    Each rocket has a DNA sequence of thrust vectors that determine its movement.
    The rocket's performance is evaluated based on how close it gets to a target.
    """
    
    def __init__(self, start_pos: Tuple[float, float], 
                 dna_length: int = RocketConfig.DEFAULT_DNA_LENGTH,
                 config: RocketConfig = None):
        """
        Initialize a new rocket.
        
        Args:
            start_pos: Starting position as (x, y) tuple
            dna_length: Number of thrust instructions in DNA sequence
            config: Configuration object (uses default if None)
        """
        # Initialize configuration
        self.config = config or RocketConfig()
        
        # Initialize physics properties using numpy for efficiency
        self.pos = np.array(start_pos, dtype=float)
        self.vel = np.zeros(2, dtype=float)
        self.acc = np.zeros(2, dtype=float)
        
        # Initialize genetic algorithm properties
        self.dna_length = dna_length
        self.dna = self._generate_random_dna()
        self.current_step = 0
        
        # Initialize evaluation properties
        self.fitness = 0.0
        self.has_reached_target = False
        self.target_reached_step = None
        
        # Initialize visual properties
        self.radius = self.config.RADIUS
        self.trail: List[np.ndarray] = []
        
        # Initialize state flags
        self.is_active = True
        self.has_collided = False
    
    def _generate_random_dna(self) -> List[np.ndarray]:
        """Generate a random DNA sequence of thrust vectors."""
        return [
            Vector2D.random_thrust_vector(
                self.config.MIN_THRUST_MAGNITUDE,
                self.config.MAX_THRUST_MAGNITUDE
            )
            for _ in range(self.dna_length)
        ]
    
    def update(self, world) -> None:
        """
        Update the rocket's state for one simulation step.
        
        Args:
            world: The simulation world containing boundaries and obstacles
        """
        if not self.is_active:
            return
        
        # Apply current DNA instruction or stop if out of fuel
        self._apply_thrust()
        
        # Update physics
        self._update_physics()
        
        # Update visual trail
        self._update_trail()
        
        # Check for collisions or boundaries
        self._check_world_interactions(world)
    
    def _apply_thrust(self) -> None:
        """Apply thrust based on current DNA instruction."""
        if self.current_step < self.dna_length:
            self.acc = self.dna[self.current_step].copy()
            self.current_step += 1
        else:
            # Out of fuel - no more thrust
            self.acc = np.zeros(2, dtype=float)
    
    def _update_physics(self) -> None:
        """Update velocity and position based on current acceleration."""
        # Apply acceleration to velocity
        self.vel += self.acc
        
        # Apply velocity damping (simulates air resistance)
        self.vel *= self.config.VELOCITY_DAMPING
        
        # Limit maximum velocity to prevent unrealistic speeds
        self.vel = Vector2D.limit_magnitude(self.vel, self.config.MAX_VELOCITY)
        
        # Update position
        self.pos += self.vel
    
    def _update_trail(self) -> None:
        """Update the visual trail with current position."""
        self.trail.append(self.pos.copy())
        
        # Limit trail length to prevent memory issues
        if len(self.trail) > self.config.MAX_TRAIL_LENGTH:
            self.trail.pop(0)
    
    def _check_world_interactions(self, world) -> None:
        """Check for collisions with world boundaries or obstacles."""
        # This method would contain collision detection logic
        # Implementation depends on the world structure
        pass
    
    def evaluate_fitness(self, target_pos: Tuple[float, float]) -> None:
        """
        Calculate and update the rocket's fitness score.
        
        Args:
            target_pos: Target position as (x, y) tuple
        """
        target_array = np.array(target_pos, dtype=float)
        distance_to_target = Vector2D.safe_distance(self.pos, target_array)
        
        # Check if rocket has reached the target
        if distance_to_target <= self.config.TARGET_RADIUS and not self.has_reached_target:
            self._handle_target_reached()
        
        # Calculate fitness based on performance
        if self.has_reached_target:
            self.fitness = self._calculate_success_fitness()
        else:
            self.fitness = self._calculate_distance_fitness(distance_to_target)
    
    def _handle_target_reached(self) -> None:
        """Handle the event when rocket reaches the target."""
        self.has_reached_target = True
        self.target_reached_step = self.current_step
        # Rocket continues moving but we remember when it reached target
    
    def _calculate_success_fitness(self) -> float:
        """Calculate fitness for rockets that reached the target."""
        # Base reward for reaching target
        base_reward = self.config.FITNESS_TARGET_REWARD
        
        # Bonus for reaching target quickly (more efficient path)
        if self.target_reached_step is not None:
            steps_remaining = self.dna_length - self.target_reached_step
            efficiency_bonus = steps_remaining * self.config.FITNESS_BONUS_PER_STEP
            return base_reward + efficiency_bonus
        
        return base_reward
    
    def _calculate_distance_fitness(self, distance: float) -> float:
        """
        Calculate fitness based on distance to target.
        
        Args:
            distance: Distance to target
            
        Returns:
            Fitness score (higher is better)
        """
        # Use inverse distance with small epsilon to avoid division by zero
        return 1.0 / (distance + np.finfo(float).eps)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the rocket for visualization or analysis.
        
        Returns:
            Dictionary containing all relevant rocket state information
        """
        return {
            'pos': self.pos.tolist(),
            'vel': self.vel.tolist(),
            'acc': self.acc.tolist(),
            'fitness': self.fitness,
            'trail': [position.tolist() for position in self.trail],
            'radius': self.radius,
            'is_active': self.is_active,
            'has_reached_target': self.has_reached_target,
            'current_step': self.current_step,
            'dna_length': self.dna_length,
            'fuel_remaining': max(0, self.dna_length - self.current_step)
        }
    
    def clone_with_dna(self, new_dna: List[np.ndarray]) -> 'Rocket':
        """
        Create a new rocket with the same configuration but different DNA.
        
        Args:
            new_dna: New DNA sequence for the cloned rocket
            
        Returns:
            New rocket instance with the provided DNA
        """
        clone = Rocket(self.pos.copy(), len(new_dna), self.config)
        clone.dna = [instruction.copy() for instruction in new_dna]
        return clone
    
    def get_dna_copy(self) -> List[np.ndarray]:
        """Get a deep copy of the rocket's DNA for genetic operations."""
        return [instruction.copy() for instruction in self.dna]

class Target(Entity):
    def __init__(self, pos, radius=20):
        self.pos = tuple(pos)
        self.radius = radius

    def update(self, world):
        pass  # Target is static by default

    def get_state(self):
        return {
            'pos': self.pos,
            'radius': self.radius
        } 