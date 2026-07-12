"""
renderer_pygame.py
Real-time graphical rendering of the maze using pygame (requirement #14: grid mode).
On-screen cell size (PIXELS_PER_CELL) is a scaled-down representation of the
real 16 cm per cell.
"""

import math

import pygame

PIXELS_PER_CELL = 20   # scaled down from the real 16 cm to 20 px on screen
WALL_THICKNESS = 2
MARGIN = 20            # space reserved for status text
HUD_HEIGHT = 60
SIGHT_LINE_DASH = 6    # length in px of each dash segment
SIGHT_LINE_GAP = 5     # length in px of each gap between dashes

COLOR_BG = (250, 248, 240)
COLOR_WALL = (40, 40, 40)
COLOR_MOUSE = (120, 70, 30)
COLOR_MOUSE_EYE = (255, 255, 255)
COLOR_CHEESE = (255, 196, 20)
COLOR_START = (180, 220, 255)
COLOR_TEXT = (20, 20, 20)
COLOR_DEAD = (200, 40, 40)
COLOR_WIN = (30, 160, 60)
COLOR_SIGHT_LINE = (220, 90, 90)


class PygameRenderer:
    def __init__(self, maze, max_computation_seconds=180):
        pygame.init()
        pygame.display.set_caption("Maze Mouse")
        board_px = maze.size * PIXELS_PER_CELL
        self.width = board_px + MARGIN * 2
        self.height = board_px + MARGIN * 2 + HUD_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont("Tahoma", 18)
        self.font_small = pygame.font.SysFont("Tahoma", 14)
        self.clock = pygame.time.Clock()
        self.max_computation_ms = max_computation_seconds * 1000

    def cell_to_px(self, r, c):
        x = MARGIN + c * PIXELS_PER_CELL
        y = MARGIN + r * PIXELS_PER_CELL
        return x, y

    def draw_walls(self, maze):
        for r in range(maze.size):
            for c in range(maze.size):
                x, y = self.cell_to_px(r, c)
                cell = maze.grid[r][c]
                if cell.walls["N"]:
                    pygame.draw.line(self.screen, COLOR_WALL, (x, y), (x + PIXELS_PER_CELL, y), WALL_THICKNESS)
                if cell.walls["W"]:
                    pygame.draw.line(self.screen, COLOR_WALL, (x, y), (x, y + PIXELS_PER_CELL), WALL_THICKNESS)
                if cell.walls["S"]:
                    pygame.draw.line(self.screen, COLOR_WALL, (x, y + PIXELS_PER_CELL),
                                      (x + PIXELS_PER_CELL, y + PIXELS_PER_CELL), WALL_THICKNESS)
                if cell.walls["E"]:
                    pygame.draw.line(self.screen, COLOR_WALL, (x + PIXELS_PER_CELL, y),
                                      (x + PIXELS_PER_CELL, y + PIXELS_PER_CELL), WALL_THICKNESS)

    def draw_start_and_cheese(self, maze):
        sx, sy = self.cell_to_px(*maze.start)
        pygame.draw.rect(self.screen, COLOR_START, (sx + 2, sy + 2, PIXELS_PER_CELL - 4, PIXELS_PER_CELL - 4))

        ex, ey = self.cell_to_px(*maze.exit)
        center = (ex + PIXELS_PER_CELL // 2, ey + PIXELS_PER_CELL // 2)
        pygame.draw.circle(self.screen, COLOR_CHEESE, center, PIXELS_PER_CELL // 3)
        # small cheese holes
        pygame.draw.circle(self.screen, COLOR_BG, (center[0] - 3, center[1] - 2), 2)
        pygame.draw.circle(self.screen, COLOR_BG, (center[0] + 2, center[1] + 3), 2)

    def draw_sight_line(self, maze, mouse):
        """Draw a dashed straight line showing the direct displacement
        between the mouse and the cheese (exit), ignoring walls."""
        mx, my = self.cell_to_px(*mouse.position)
        start = (mx + PIXELS_PER_CELL // 2, my + PIXELS_PER_CELL // 2)
        ex, ey = self.cell_to_px(*maze.exit)
        end = (ex + PIXELS_PER_CELL // 2, ey + PIXELS_PER_CELL // 2)

        dx, dy = end[0] - start[0], end[1] - start[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        ux, uy = dx / distance, dy / distance

        step = SIGHT_LINE_DASH + SIGHT_LINE_GAP
        travelled = 0.0
        while travelled < distance:
            seg_start = (start[0] + ux * travelled, start[1] + uy * travelled)
            seg_end_dist = min(travelled + SIGHT_LINE_DASH, distance)
            seg_end = (start[0] + ux * seg_end_dist, start[1] + uy * seg_end_dist)
            pygame.draw.line(self.screen, COLOR_SIGHT_LINE, seg_start, seg_end, 2)
            travelled += step

    def draw_mouse(self, mouse):
        x, y = self.cell_to_px(*mouse.position)
        cx, cy = x + PIXELS_PER_CELL // 2, y + PIXELS_PER_CELL // 2
        radius = PIXELS_PER_CELL // 2 - 3
        pygame.draw.circle(self.screen, COLOR_MOUSE, (cx, cy), radius)

        # nose/facing direction, shown as a small dot at the front
        offset = {"N": (0, -radius), "S": (0, radius), "E": (radius, 0), "W": (-radius, 0)}[mouse.heading]
        nose = (cx + offset[0], cy + offset[1])
        pygame.draw.circle(self.screen, COLOR_MOUSE_EYE, nose, 3)

    def draw_hud(self, mouse, status_text="", total_elapsed=0.0):
        y_base = self.height - HUD_HEIGHT
        pygame.draw.rect(self.screen, (235, 235, 225), (0, y_base, self.width, HUD_HEIGHT))
        computation_ms = mouse.total_computation_time * 1000
        info = (f"Step: {mouse.moves_count}   "
                 f"Total time (real): {total_elapsed:.3f}s   "
                 f"Computation time (algo): {computation_ms:.2f}ms / {self.max_computation_ms:.0f}ms   "
                 f"Heading: {mouse.heading}")
        text_surf = self.font_small.render(info, True, COLOR_TEXT)
        self.screen.blit(text_surf, (MARGIN, y_base + 6))

        if status_text:
            color = COLOR_WIN if "Success" in status_text else COLOR_DEAD
            status_surf = self.font.render(status_text, True, color)
            self.screen.blit(status_surf, (MARGIN, y_base + 28))

    def render(self, maze, mouse, status_text="", total_elapsed=0.0):
        # drain the event queue so the app doesn't hang (allows closing the window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        self.screen.fill(COLOR_BG)
        self.draw_sight_line(maze, mouse)
        self.draw_start_and_cheese(maze)
        self.draw_walls(maze)
        self.draw_mouse(mouse)
        self.draw_hud(mouse, status_text, total_elapsed)
        pygame.display.flip()

    def save_screenshot(self, path):
        pygame.image.save(self.screen, path)

    def tick(self, fps=30):
        self.clock.tick(fps)

    def wait_and_close(self, seconds=3):
        pygame.time.wait(int(seconds * 1000))
        pygame.quit()
