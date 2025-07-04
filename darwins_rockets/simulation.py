import pygame
import sys
import math
from darwins_rockets.rocket import Target
from darwins_rockets.world import World
import numpy as np
from config import (
    SIM_WIDTH, SIM_HEIGHT, NUM_ROCKETS, DNA_LENGTH, MUTATION_RATE, OUT_OF_BOUNDS_TIMEOUT, FPS,
    LINE_GAP, TITLE_OFFSET, SUBTITLE_EXTRA_OFFSET, PARAM_SECTION_EXTRA_OFFSET, BUTTON_SECTION_EXTRA_SPACE,
    BUTTONS_HEADER_OFFSET, BUTTONS_EXTRA_OFFSET, PROGRESS_BAR_EXTRA_OFFSET, STATISTICS_HEADER_OFFSET,
    WINDOW_HEADER_OFFSET, INSTRUCTIONS_HEADER_OFFSET, SHORTCUTS_HEADER_OFFSET, SHORTCUTS_ROW_OFFSET,
    SHORTCUTS_EXTRA_OFFSET, ELAPSED_TIME_EXTRA_OFFSET, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, START_POS_Y_OFFSET,
    START_POS_LINE_OFFSET1, START_POS_LINE_OFFSET2,
    WHITE, RED, BLUE, TARGET_RADIUS, ROCKET_RADIUS, BG_COLOR, BG_DARK,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ACCENT, TARGET_COLOR, TARGET_HOVER,
    DIVIDER_COLOR, DIVIDER_WIDTH
)

class Simulation:
    WIDTH = SIM_WIDTH
    HEIGHT = SIM_HEIGHT
    WHITE = WHITE
    RED = RED
    BLUE = BLUE
    TARGET_RADIUS = TARGET_RADIUS
    ROCKET_RADIUS = ROCKET_RADIUS
    NUM_ROCKETS = NUM_ROCKETS
    DNA_LENGTH = DNA_LENGTH
    OUT_OF_BOUNDS_TIMEOUT = OUT_OF_BOUNDS_TIMEOUT
    FPS = FPS
    BG_COLOR = BG_COLOR
    BG_DARK = BG_DARK
    TEXT_PRIMARY = TEXT_PRIMARY
    TEXT_SECONDARY = TEXT_SECONDARY
    TEXT_ACCENT = TEXT_ACCENT
    TARGET_COLOR = TARGET_COLOR
    TARGET_HOVER = TARGET_HOVER
    DIVIDER_COLOR = DIVIDER_COLOR
    DIVIDER_WIDTH = DIVIDER_WIDTH
    INFO_PANEL_WIDTH = 340
    PANEL_HEIGHT = 220
    PANEL_GAP = 12

    def __init__(self):
        pygame.init()
        # Create resizable window
        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Darwin's Rockets - Genetic Algorithm Simulation")
        # Multiple font sizes for better typography
        self.font_large = pygame.font.SysFont(None, 36)
        self.font = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 22)
        self.clock = pygame.time.Clock()
        self.ROCKET_START_POSITIONS = [
            (int((i + 1) * self.WIDTH / (self.NUM_ROCKETS + 1)), self.HEIGHT - 50)
            for i in range(self.NUM_ROCKETS)
        ]
        # --- World integration ---
        self.world = World(self.WIDTH, self.HEIGHT, population_size=self.NUM_ROCKETS, dna_length=self.DNA_LENGTH, mutation_rate=0.03)
        self.world.set_target(self.WIDTH // 2, self.HEIGHT // 4, radius=self.TARGET_RADIUS)
        self.generation = 1
        self.best_fitness = 0
        self.elapsed_time = 0.0
        self.paused = False
        self.running = False
        self.show_dashboard = True
        # Generation statistics for testing and tuning
        self.generation_stats = {
            'total_rockets_reached_target': 0,
            'generations_with_success': 0,
            'best_generation': 1,
            'best_distance_achieved': float('inf')
        }
        # Target dragging functionality
        self.dragging_target = False
        self.target_hovered = False
        # Window management
        self.window_width = self.WIDTH
        self.window_height = self.HEIGHT
        self.min_width = 800  # Minimum window width
        self.min_height = 600  # Minimum window height
        # Simplified view - always show both simulation and dashboard
        self.selected_rocket = None
        self.step_once = False

    def is_mouse_over_target(self, mouse_pos):
        """Check if mouse position is over the target"""
        target_center = pygame.Vector2(self.world.target_pos)
        mouse_pos_vec = pygame.Vector2(mouse_pos)
        return mouse_pos_vec.distance_to(target_center) <= self.TARGET_RADIUS

    def update_target_position(self, mouse_pos):
        """Update target position to mouse position, keeping it within bounds"""
        x = max(self.TARGET_RADIUS, min(mouse_pos[0], self.WIDTH - self.TARGET_RADIUS))
        y = max(self.TARGET_RADIUS, min(mouse_pos[1], self.HEIGHT - self.TARGET_RADIUS))
        self.world.set_target(x, y, radius=self.TARGET_RADIUS)

    def draw_message(self, text):
        # Draw message with better styling and background
        msg = self.font_large.render(text, True, (255, 255, 255))
        rect = msg.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        
        # Draw background for better readability
        bg_rect = rect.inflate(40, 20)
        pygame.draw.rect(self.WIN, (0, 0, 0, 150), bg_rect, border_radius=10)
        pygame.draw.rect(self.WIN, (255, 255, 255, 50), bg_rect, 2, border_radius=10)
        
        self.WIN.blit(msg, rect)

    def draw_fitness(self, rocket, normalized_fitness):
        # Display normalized fitness (0.00 to 1.00) with better styling
        fitness_text = f"{normalized_fitness:.4f}"
        
        # Choose font size based on fitness value
        if normalized_fitness > 0.8:
            font = self.font
            text_color = (255, 255, 255)  # White for high fitness
        else:
            font = self.font_small
            text_color = (200, 200, 200)  # Light gray for lower fitness
        
        msg = font.render(fitness_text, True, text_color)
        
        # Position above rocket with slight offset
        pos = (int(rocket.pos[0]), int(rocket.pos[1]) - rocket.radius - 25)
        rect = msg.get_rect(center=pos)
        
        # Draw background for better readability
        bg_rect = rect.inflate(8, 4)
        pygame.draw.rect(self.WIN, (0, 0, 0, 100), bg_rect, border_radius=4)
        
        self.WIN.blit(msg, rect)

    def restart(self):
        self.world = World(self.WIDTH, self.HEIGHT, population_size=self.NUM_ROCKETS, dna_length=self.DNA_LENGTH, mutation_rate=0.03)
        self.world.set_target(self.WIDTH // 2, self.HEIGHT // 4, radius=self.TARGET_RADIUS)
        self.paused = False

    def get_normalized_fitness(self, rocket, min_fitness, max_fitness):
        if max_fitness > min_fitness:
            return (rocket.fitness - min_fitness) / (max_fitness - min_fitness)
        return 0.0

    def get_rocket_color(self, rocket, min_fitness, max_fitness):
        # If rocket reached the target, color is green
        dist = math.hypot(rocket.pos[0] - self.world.target_pos[0], rocket.pos[1] - self.world.target_pos[1])
        if dist <= self.TARGET_RADIUS:
            return (0, 255, 0)
        # Use normalized fitness for color mapping
        norm = self.get_normalized_fitness(rocket, min_fitness, max_fitness)
        # Interpolate from red to green
        r = int(255 * (1 - norm))
        g = int(255 * norm)
        # Clamp values to 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        return (r, g, 0)

    def draw_simulation_area(self, surface, rect):
        # Draw a subtle gradient background
        bg_color_top = (210, 215, 230)
        bg_color_bottom = (180, 185, 210)
        for y in range(rect.height):
            blend = y / rect.height
            color = (
                int(bg_color_top[0] * (1 - blend) + bg_color_bottom[0] * blend),
                int(bg_color_top[1] * (1 - blend) + bg_color_bottom[1] * blend),
                int(bg_color_top[2] * (1 - blend) + bg_color_bottom[2] * blend),
            )
            pygame.draw.line(surface, color, (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
        # Draw simulation content
        prev_clip = surface.get_clip()
        self.draw_simulation_content()
        surface.set_clip(prev_clip)

    def start_sim(self):
        self.running = True
        self.paused = False

    def pause_sim(self):
        # If already paused, set step_once to True to advance one frame
        if self.paused:
            self.step_once = True
        else:
            self.paused = True

    def quit_sim(self):
        pygame.quit()
        sys.exit()

    def draw_simulation_content(self):
        """Draw the main simulation content"""
        # Draw background elements
        self.draw_background_grid()
        self.draw_simulation_boundaries()
        self.draw_start_positions()
        # Draw title for the main simulation area
        self.draw_simulation_title()
        # Draw all entities in the world
        for entity in self.world.get_entities():
            if isinstance(entity, Target):
                target_color = self.TARGET_HOVER if self.target_hovered else self.TARGET_COLOR
                target_radius = self.TARGET_RADIUS + 3 if self.target_hovered else self.TARGET_RADIUS
                # Draw target glow effect
                if self.target_hovered:
                    pygame.draw.circle(self.WIN, (255, 255, 255, 50), entity.pos, target_radius + 8)
                # Draw target
                pygame.draw.circle(self.WIN, target_color, entity.pos, target_radius)
                pygame.draw.circle(self.WIN, (255, 255, 255), entity.pos, target_radius - 5, 2)
                # Draw target center
                pygame.draw.circle(self.WIN, (255, 255, 255), entity.pos, 3)
            elif hasattr(entity, 'fitness'):
                stats = self.world.get_stats()
                min_fitness = 0
                max_fitness = stats.get('best_fitness_current_gen', 1)
                normalized_fitness = (entity.fitness - min_fitness) / (max_fitness - min_fitness) if max_fitness > min_fitness else 0.0
                color = self.get_rocket_color(entity, min_fitness, max_fitness)
                trail = getattr(entity, 'trail', [])
                if len(trail) > 1:
                    for i in range(len(trail) - 1):
                        alpha = int(255 * (i / len(trail)))
                        trail_color = (*color[:3], alpha)
                        start = trail[i]
                        end = trail[i + 1]
                        pygame.draw.line(self.WIN, trail_color, start, end, 2)
                pos = entity.pos
                pygame.draw.circle(self.WIN, color, (int(pos[0]), int(pos[1])), entity.radius)
                vel = getattr(entity, 'vel', np.zeros(2))
                if np.linalg.norm(vel) > 0.1:
                    direction = vel / np.linalg.norm(vel)
                    end_pos = (pos[0] + direction[0] * (entity.radius + 5), pos[1] + direction[1] * (entity.radius + 5))
                    pygame.draw.line(self.WIN, (255, 255, 255), pos, end_pos, 2)
                    arrow_size = 4
                    perp = (-direction[1], direction[0])
                    arrow1 = (end_pos[0] - direction[0] * arrow_size + perp[0] * arrow_size,
                              end_pos[1] - direction[1] * arrow_size + perp[1] * arrow_size)
                    arrow2 = (end_pos[0] - direction[0] * arrow_size - perp[0] * arrow_size,
                              end_pos[1] - direction[1] * arrow_size - perp[1] * arrow_size)
                    pygame.draw.polygon(self.WIN, (255, 255, 255), [end_pos, arrow1, arrow2])
                pygame.draw.circle(self.WIN, (255, 255, 255), (int(pos[0]), int(pos[1])), 2)
                self.draw_fitness(entity, normalized_fitness)
        # If simulation is not running, show message
        if not (self.running and not self.paused):
            self.draw_message("All rockets out of bounds! Press R to restart or Q to quit.")

    def draw_background_grid(self):
        """Draw a subtle grid pattern in the background (main area only)"""
        grid_color = (230, 230, 235)  # Very light blue-gray
        grid_spacing = 50
        
        # Vertical lines (only in main area)
        for x in range(0, self.WIDTH, grid_spacing):
            pygame.draw.line(self.WIN, grid_color, (x, 0), (x, self.HEIGHT), 1)
        
        # Horizontal lines (only in main area)
        for y in range(0, self.HEIGHT, grid_spacing):
            pygame.draw.line(self.WIN, grid_color, (0, y), (self.WIDTH, y), 1)
    
    def draw_simulation_boundaries(self):
        """Draw boundary lines around the main simulation area"""
        boundary_color = (200, 200, 210)  # Light gray-blue
        pygame.draw.rect(self.WIN, boundary_color, (0, 0, self.WIDTH, self.HEIGHT), 2)
    
    def draw_start_positions(self):
        """Draw markers for rocket start positions"""
        for pos in self.ROCKET_START_POSITIONS:
            # Draw a small circle at each start position
            pygame.draw.circle(self.WIN, (180, 180, 200), pos, 3)
            # Draw a subtle line to show the starting area
            pygame.draw.line(self.WIN, (180, 180, 200), (pos[0], pos[1] + 10), (pos[0], pos[1] + 30), 1)
    
    def draw_simulation_title(self):
        """Draw title for the main simulation area"""
        title = self.font_large.render("SIMULATION AREA", True, (80, 80, 100))
        title_rect = title.get_rect(center=(self.WIDTH // 2, 25))
        
        # Draw background for title
        bg_rect = title_rect.inflate(40, 10)
        pygame.draw.rect(self.WIN, (255, 255, 255, 200), bg_rect, border_radius=8)
        pygame.draw.rect(self.WIN, (200, 200, 210), bg_rect, 2, border_radius=8)
        
        self.WIN.blit(title, title_rect)

    def handle_window_resize(self, new_width, new_height):
        """Handle window resize events"""
        # Enforce minimum size
        new_width = max(self.min_width, new_width)
        new_height = max(self.min_height, new_height)
        
        # Update window dimensions
        self.window_width = new_width
        self.window_height = new_height
        
        # Resize the window
        self.WIN = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        
        # Update layout based on new size
        self.update_layout_for_size(new_width, new_height)

    def update_layout_for_size(self, width, height):
        """Update layout parameters based on window size"""
        # Calculate new dimensions
        if width < 1000:  # Small window - use compact layout
            self.WIDTH = width
        else:  # Large window - use spacious layout
            self.WIDTH = width
        
        # Update height
        self.HEIGHT = height
        
        # Update target position to be proportional
        self.world.set_target(self.WIDTH // 2, self.HEIGHT // 4, radius=self.TARGET_RADIUS)
        
        # Update rocket start positions
        self.ROCKET_START_POSITIONS = [
            (int((i + 1) * self.WIDTH / (self.NUM_ROCKETS + 1)), self.HEIGHT - 50)
            for i in range(self.NUM_ROCKETS)
        ] 

        # Update population with new positions
        if hasattr(self, 'world'):
            self.world = World(self.WIDTH, self.HEIGHT, population_size=self.NUM_ROCKETS, dna_length=self.DNA_LENGTH, mutation_rate=0.03)
            self.world.set_target(self.WIDTH // 2, self.HEIGHT // 4, radius=self.TARGET_RADIUS)
        
        # Update rocket bounds checking
        self.update_rocket_bounds()

    def update_rocket_bounds(self):
        """Update rocket bounds checking with current window dimensions"""
        rockets = self.world.get_rockets()
        for rocket in rockets:
            # Update fitness with current bounds
            rocket.evaluate_fitness(self.world.target_pos)
            # Check if rocket is out of bounds with current window size
            if rocket.pos[0] > self.WIDTH or rocket.pos[1] > self.HEIGHT:
                rocket.fitness *= 0.1  # 90% penalty for out of bounds 

    def run(self):
        while True:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.elapsed_time += dt if self.running and not self.paused else 0
            # --- ADVANCE SIMULATION LOGIC ---
            if self.running and (not self.paused or self.step_once):
                self.world.step()  # Advance all entities (rockets, etc.)
                if self.step_once:
                    self.step_once = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.handle_window_resize(event.w, event.h)
                if event.type == pygame.MOUSEBUTTONDOWN:
                     if event.button == 1:
                        if self.is_mouse_over_target(event.pos):
                            self.dragging_target = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_target = False
                if event.type == pygame.MOUSEMOTION:
                    if self.dragging_target:
                        if event.pos[0] <= self.WIDTH:
                            self.update_target_position(event.pos)
                        else:
                            self.dragging_target = False
                    if event.pos[0] <= self.WIDTH:
                        self.target_hovered = self.is_mouse_over_target(event.pos)
                    else:
                        self.target_hovered = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.start_sim()
                    elif event.key == pygame.K_p:
                        self.pause_sim()
                    elif event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_q:
                        self.quit_sim()
            # --- Layout calculation ---
            win_width, win_height = self.WIN.get_size()
            sim_rect = pygame.Rect(0,0, win_width, win_height)
            # --- Drawing ---
            self.WIN.fill((200, 205, 220))
            self.draw_simulation_area(self.WIN, sim_rect)
            pygame.display.flip() 