# Darwin's Rockets 🚀

A Python-based educational simulation that demonstrates genetic algorithms through an interactive rocket navigation game. Watch as rockets evolve over generations to reach a target using principles inspired by natural selection.

![Darwin's Rockets Simulation](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green.svg)
![Genetic Algorithm](https://img.shields.io/badge/Algorithm-Genetic-orange.svg)

## 🧬 Theory Behind the Implementation

### Genetic Algorithm Fundamentals

Darwin's Rockets implements a **genetic algorithm**, a computational method inspired by biological evolution. The core concept is that solutions to problems can be "evolved" through:

1. **Selection**: Better-performing solutions are more likely to be chosen as parents
2. **Crossover**: Combining traits from two parent solutions to create offspring
3. **Mutation**: Random changes to introduce new genetic material
4. **Fitness Evaluation**: Measuring how well each solution performs

### The Rocket Navigation Problem

In this simulation, each rocket has a "DNA" sequence consisting of thrust vectors (direction and magnitude) that determine its movement pattern. The goal is to evolve rockets that can efficiently navigate from a starting position to a target.

**Key Concepts:**
- **DNA**: A sequence of thrust instructions (vectors) that control rocket movement
- **Fitness**: How close the rocket gets to the target (inverse distance)
- **Generation**: A complete cycle where all rockets attempt the task
- **Evolution**: Using the best performers to create the next generation

### Fitness Function

The fitness calculation rewards:
- **Target Achievement**: Large bonus (1000 points) for reaching the target
- **Efficiency**: Bonus points for reaching the target with fuel remaining
- **Distance**: Inverse distance to target for rockets that don't reach it
- **Penalties**: Reduced fitness for rockets that go out of bounds

## 🏗️ Implementation Architecture

### Core Components

The package is organized into several key modules:

#### 1. **Simulation** (`simulation.py`)
- **Purpose**: Main game loop and visualization engine
- **Responsibilities**:
  - Pygame window management and rendering
  - User interaction handling (mouse, keyboard)
  - Real-time visualization of rockets and target

#### 2. **World** (`world.py`)
- **Purpose**: Simulation environment and generation management
- **Responsibilities**:
  - Managing all entities (rockets, targets)
  - Coordinating the genetic algorithm lifecycle
  - Tracking generation progress and statistics
  - Handling world boundaries and physics

#### 3. **Rocket** (`rocket.py`)
- **Purpose**: Individual rocket entities with physics and DNA
- **Responsibilities**:
  - Physics simulation (position, velocity, acceleration)
  - DNA-based movement control
  - Fitness evaluation
  - Visual trail management

#### 4. **Population** (`population.py`)
- **Purpose**: Genetic algorithm operations
- **Responsibilities**:
  - DNA crossover and mutation
  - Parent selection (roulette wheel)
  - Generation evolution
  - Fitness normalization

#### 5. **Configuration** (`config.py`)
- **Purpose**: Centralized parameter management
- **Responsibilities**:
  - Simulation parameters (population size, DNA length)
  - Physics constants (velocity damping, thrust limits)
  - Visual settings (colors, dimensions)
  - Genetic algorithm parameters (mutation rate)

### Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Simulation    │───▶│     World       │───▶│   Population    │
│   (UI/Events)   │    │ (Environment)   │    │ (Genetic Ops)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rocket        │    │     Target      │    │     DNA         │
│ (Physics/DNA)   │    │   (Static)      │    │ (Instructions)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 How Components Work Together

### 1. **Initialization Phase**
```python
# Main entry point
sim = Simulation()  # Creates Pygame window and UI
world = World(...)  # Sets up environment with population
population = Population(...)  # Initializes random DNA sequences
rockets = [Rocket(...) for _ in range(population_size)]  # Creates rockets
```

### 2. **Generation Lifecycle**
1. **Spawn**: World creates rockets with DNA from population
2. **Execute**: Each rocket follows its DNA sequence for movement
3. **Evaluate**: Fitness calculated based on final position
4. **Evolve**: Population uses genetic operations to create next generation
5. **Repeat**: New generation spawns with evolved DNA

### 3. **Real-time Simulation Loop**
*Note: This is a simplified conceptual illustration. The actual implementation includes detailed Pygame event handling, window management, and timing controls.*

```python
while running:
    # Handle user input (mouse, keyboard)
    handle_events()
    
    # Update physics and movement
    world.step()  # Updates all rockets
    
    # Render visualization
    draw_simulation()
    
    # Check generation completion
    if generation_complete:
        evolve_population()
        spawn_new_generation()
```

*The actual main loop in `simulation.py` handles Pygame events, window resizing, mouse interactions, keyboard controls, timing, pause functionality, and detailed rendering - much more complex than this simplified version.*

### 4. **Genetic Operations Flow**
1. **Selection**: Roulette wheel selects parents based on fitness
2. **Crossover**: DNA sequences are combined at random points
3. **Mutation**: Random genes are replaced with new random values
4. **Replacement**: New DNA sequences replace the population

## 🚀 How to Run the Project

### Prerequisites

- **Python 3.8+**
- **Pixi** (package manager) - [Install Pixi](https://pixi.sh/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd darwins_rockets
   ```

2. **Install dependencies using Pixi:**
   ```bash
   pixi install
   ```

3. **Activate the environment:**
   ```bash
   pixi shell
   ```

### Running the Simulation

1. **Start the simulation:**
   ```bash
   python main.py
   ```

2. **Alternative: Use Pixi task:**
   ```bash
   pixi run python main.py
   ```

### Development Setup

For development with PyCharm:
```bash
pixi run pixi-pycharm
```

## 🎮 How to Operate the Project

### Basic Controls

| Key | Action |
|-----|--------|
| `S` | Start/Resume simulation |
| `P` | Pause simulation (press again for step-by-step) |
| `R` | Restart simulation with new random population |
| `Q` | Quit the application |

### Mouse Interactions

- **Drag Target**: Click and drag the red target to reposition it
- **Hover Effects**: Target glows when you hover over it

### Understanding the Display

#### Visual Elements
- **Rockets**: Colored circles with trails
  - **Green**: Successfully reached target
  - **Red to Green gradient**: Based on fitness (red = low, green = high)
  - **White arrow**: Current velocity direction
  - **Trail**: Movement history (fades over time)

- **Target**: Red circle with white border
- **Start Positions**: Small markers at bottom of screen
- **Grid**: Background reference lines

#### Fitness Display
- **Numbers above rockets**: Normalized fitness (0.0000 to 1.0000)
- **Color coding**: Visual representation of performance

### Interpreting Results

#### Generation Progress
- Watch how rocket colors change from red to green over generations
- Observe trails becoming more direct and efficient
- Notice rockets reaching the target more frequently

#### Performance Indicators
- **Fitness scores**: Higher numbers indicate better performance
- **Target hits**: Count of rockets reaching the target
- **Trail efficiency**: More direct paths indicate better evolution

### Parameter Tuning

You can modify `config.py` to experiment with different parameters:

```python
# Genetic Algorithm Parameters
NUM_ROCKETS = 10          # Population size
DNA_LENGTH = 500          # Number of thrust instructions
MUTATION_RATE = 0.03      # Probability of gene mutation

# Physics Parameters
MAX_VELOCITY = 5.0        # Maximum rocket speed
VELOCITY_DAMPING = 0.98   # Air resistance simulation
```

## 🔮 Ideas for Future Development

### 1. **Enhanced Genetic Algorithms**
- **Tournament Selection**: Alternative to roulette wheel selection
- **Multi-point Crossover**: More complex DNA recombination
- **Adaptive Mutation**: Mutation rate that changes based on population diversity

### 2. **Multiple Objectives**
- **Multi-target Navigation**: Rockets must visit multiple targets
- **Time Constraints**: Bonus for reaching target within time limits
- **Energy Efficiency**: Reward for using minimal fuel

### 3. **Educational Enhancements**
- **Tutorial Mode**: Step-by-step explanation of genetic algorithm concepts
- **Algorithm Visualization**: Show selection, crossover, and mutation processes
- **Interactive Lessons**: Built-in educational content

### 4. **Research Applications**
- **Pathfinding Algorithms**: Compare with A*, RRT, and other algorithms
- **Neural Network Integration**: Combine with neural evolution
- **Real-world Applications**: Robot navigation, drone path planning

## 📊 Performance Tips

### For Better Evolution
- **Increase Population Size**: More genetic diversity
- **Adjust Mutation Rate**: Higher rates for exploration, lower for exploitation
- **Extend DNA Length**: More complex movement patterns
- **Modify Fitness Function**: Experiment with different reward structures

### For Smoother Performance
- **Reduce Trail Length**: Lower `MAX_TRAIL_LENGTH` in config
- **Decrease Population Size**: Fewer rockets to simulate
- **Lower FPS**: Reduce frame rate for slower computers
- **Disable Visual Effects**: Simplify rendering for better performance

## 🤝 Contributing

Contributions are welcome! Areas that need help:
- Bug fixes and performance improvements
- New genetic algorithm implementations
- Enhanced visualization features
- Documentation improvements
- Educational content creation

## 📄 License

This project is open source. See the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Daniel Shiffman's ["Nature of Code"](https://natureofcode.com/) genetic algorithm examples
- Built with [Pygame](https://www.pygame.org/) for accessible game development
- Uses [NumPy](https://numpy.org/) for efficient numerical computations
- Managed with [Pixi](https://pixi.sh/) for reproducible development environments

---

**Happy evolving! 🧬🚀** 