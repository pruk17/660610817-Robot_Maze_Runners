"""
renderer_pygame.py
Real-time graphical rendering of the maze using pygame (requirement #14: grid mode).
On-screen cell size (PIXELS_PER_CELL) is a scaled-down representation of the
real 16 cm per cell. A silver HUD panel on the left shows the solver mode
and all live stats.
"""

import math

import pygame

PIXELS_PER_CELL = 20   # scaled down from the real 16 cm to 20 px on screen
WALL_THICKNESS = 2
MARGIN = 20
HUD_WIDTH = 200        # left panel width
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
COLOR_WIN = (30, 140, 60)
COLOR_SIGHT_LINE = (220, 90, 90)
COLOR_HUD_BG = (192, 192, 192)      # silver
COLOR_HUD_BORDER = (150, 150, 150)
COLOR_HEADER = (70, 70, 85)         # section header color (rendered bold)

HEADING_ARROW = {"N": "^", "S": "v", "E": ">", "W": "<"}

# Retro pixel-art portrait of the mouse (16x15 grid), drawn Doom-style
# in a beveled frame at the bottom of the HUD. Each character is one
# "pixel": B = dark outline, b = fur, p = pink (ears/nose), e = eye,
# w = white. The base sprite is the "happy" face; other emotions patch
# individual rows (eyes rows 7-8, nose rows 9-10, mouth rows 11-12).
MOUSE_SPRITE = [
    "..BBB......BBB..",
    ".BbbbB....BbbbB.",
    ".BbppbB..BbppbB.",
    ".BbppbB..BbppbB.",
    "..BbbBBBBBBbbB..",
    "..BbbbbbbbbbbB..",
    ".BbbbbbbbbbbbbB.",
    ".BbbwebbbbwebbB.",
    ".BbbeebbbbeebbB.",
    ".BbbbbbppbbbbbB.",
    ".BbbbbBppBbbbbB.",
    "..BbbbBwwBbbbB..",
    "..BbbbbwwbbbbB..",
    "...BBbbbbbbBB...",
    ".....BBBBBB.....",
]
EMOTION_PATCHES = {
    # far from the cheese: flat, unimpressed mouth
    "neutral": {
        11: "..BbbbBBBBbbbB..",
        12: "..BbbbbbbbbbbB..",
    },
    # mid distance: the base sprite already smiles -- no patch needed
    "happy": {},
    # close to the cheese: squinting happy eyes + big toothy grin
    "grin": {
        8: ".BbbbbbbbbbbbbB.",
        11: ".BbbBwwwwwwBbbB.",
        12: "..BbBwwwwwwBbB..",
    },
    # computation time ran out: flat dead eyes, mouth open in shock
    "dead": {
        7: ".BbbBBbbbbBBbbB.",
        8: ".BbbbbbbbbbbbbB.",
        10: ".BbbbbBeeBbbbbB.",
        11: "..BbbbBeeBbbbB..",
        12: "..BbbbbBBbbbbB..",
    },
    # reached the cheese: heart-shaped eyes + the big toothy grin
    "love": {
        6: ".BhhbhhbbhhbhhB.",
        7: ".BhhhhhbbhhhhhB.",
        8: ".BbhhhbbbbhhhbB.",
        9: ".BbbhbbppbbhbbB.",
        11: ".BbbBwwwwwwBbbB.",
        12: "..BbBwwwwwwBbB..",
    },
}
SPRITE_PALETTE = {
    "B": (60, 40, 25),
    "b": (120, 70, 30),
    "p": (240, 150, 160),
    "e": (25, 20, 20),
    "w": (255, 255, 255),
    "h": (235, 70, 100),   # heart eyes on the victory face
}
SPRITE_SCALE = 8   # 1 sprite pixel = 8 screen px (retro chunky look)

# Doom-style bezel colors for the portrait frame
COLOR_FRAME_BASE = (100, 100, 100)
COLOR_FRAME_LIGHT = (160, 160, 160)
COLOR_FRAME_DARK = (55, 55, 55)
COLOR_FRAME_INNER = (58, 54, 48)    # dark recessed background behind the face
COLOR_WHISKER = (205, 205, 205)


class PygameRenderer:
    def __init__(self, maze, max_computation_seconds=180, solver_name=""):
        pygame.init()
        pygame.display.set_caption("Maze Mouse")
        self.maze = maze  # kept for the portrait's distance-based emotion
        board_px = maze.size * PIXELS_PER_CELL
        self.width = HUD_WIDTH + MARGIN + board_px + MARGIN
        self.height = board_px + MARGIN * 2
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font_mode = pygame.font.SysFont("Tahoma", 18, bold=True)
        self.font_header = pygame.font.SysFont("Tahoma", 12, bold=True)
        self.font_value = pygame.font.SysFont("Tahoma", 15)
        self.font_status = pygame.font.SysFont("Tahoma", 14, bold=True)
        self.clock = pygame.time.Clock()
        self.max_computation_ms = max_computation_seconds * 1000
        self.solver_name = solver_name or "-"

    def cell_to_px(self, r, c):
        x = HUD_WIDTH + MARGIN + c * PIXELS_PER_CELL
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

    def _hud_section(self, y, header, value_lines):
        """Draw one HUD section (bold header + value lines), return next y."""
        pad_x = 14
        head_surf = self.font_header.render(header, True, COLOR_HEADER)
        self.screen.blit(head_surf, (pad_x, y))
        y += head_surf.get_height() + 2
        for line in value_lines:
            val_surf = self.font_value.render(line, True, COLOR_TEXT)
            self.screen.blit(val_surf, (pad_x, y))
            y += val_surf.get_height() + 2
        return y + 12  # gap before the next section

    def _wrap_text(self, text, font, max_width):
        """Simple word-wrap: split text into lines fitting max_width."""
        lines = []
        current = ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if font.size(trial)[0] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _emotion(self, mouse):
        """Pick the face to show from the remaining straight-line
        displacement to the cheese, Doom-status-bar style."""
        if not mouse.alive:
            return "dead"
        er, ec = self.maze.exit
        r, c = mouse.position
        if (r, c) == (er, ec):
            return "love"  # made it to the cheese -- heart eyes
        sr, sc = self.maze.start
        total = math.hypot(er - sr, ec - sc)
        remaining = math.hypot(er - r, ec - c)
        ratio = remaining / total if total else 0.0
        if ratio <= 0.33:
            return "grin"
        if ratio <= 0.66:
            return "happy"
        return "neutral"

    def draw_mouse_portrait(self, mouse):
        """Doom-style beveled frame with a big pixel-art mouse face whose
        emotion tracks the remaining distance to the cheese."""
        sprite_w = len(MOUSE_SPRITE[0]) * SPRITE_SCALE
        sprite_h = len(MOUSE_SPRITE) * SPRITE_SCALE
        pad = 14
        frame_w = sprite_w + pad * 2
        frame_h = sprite_h + pad * 2
        fx = (HUD_WIDTH - frame_w) // 2
        fy = self.height - frame_h - 14

        # raised metal bezel: light top/left edge, dark bottom/right edge
        pygame.draw.rect(self.screen, COLOR_FRAME_BASE, (fx, fy, frame_w, frame_h))
        pygame.draw.rect(self.screen, COLOR_FRAME_LIGHT, (fx, fy, frame_w, frame_h), 2)
        pygame.draw.line(self.screen, COLOR_FRAME_DARK,
                          (fx + 1, fy + frame_h - 1), (fx + frame_w - 1, fy + frame_h - 1), 2)
        pygame.draw.line(self.screen, COLOR_FRAME_DARK,
                          (fx + frame_w - 1, fy + 1), (fx + frame_w - 1, fy + frame_h - 1), 2)

        # recessed dark slot the face sits in (inverse bevel)
        ix, iy = fx + 6, fy + 6
        iw, ih = frame_w - 12, frame_h - 12
        pygame.draw.rect(self.screen, COLOR_FRAME_INNER, (ix, iy, iw, ih))
        pygame.draw.line(self.screen, COLOR_FRAME_DARK, (ix, iy), (ix + iw, iy), 2)
        pygame.draw.line(self.screen, COLOR_FRAME_DARK, (ix, iy), (ix, iy + ih), 2)

        # assemble the face for the current emotion
        emotion = self._emotion(mouse)
        rows = list(MOUSE_SPRITE)
        for idx, patched_row in EMOTION_PATCHES.get(emotion, {}).items():
            rows[idx] = patched_row

        x0 = fx + (frame_w - sprite_w) // 2
        y0 = fy + (frame_h - sprite_h) // 2
        for row_idx, row in enumerate(rows):
            for col_idx, ch in enumerate(row):
                color = SPRITE_PALETTE.get(ch)
                if color:
                    pygame.draw.rect(self.screen, color,
                                      (x0 + col_idx * SPRITE_SCALE,
                                       y0 + row_idx * SPRITE_SCALE,
                                       SPRITE_SCALE, SPRITE_SCALE))

        # whiskers, three per side at nose level (light so they read on
        # the dark recessed background)
        wy = y0 + 9 * SPRITE_SCALE
        for i, dy in enumerate((-7, 1, 9)):
            spread = (i - 1) * 4
            pygame.draw.line(self.screen, COLOR_WHISKER,
                              (x0 - 2, wy + dy), (x0 - 11, wy + dy + spread), 1)
            pygame.draw.line(self.screen, COLOR_WHISKER,
                              (x0 + sprite_w + 2, wy + dy),
                              (x0 + sprite_w + 11, wy + dy + spread), 1)

    def draw_hud(self, mouse, status_text="", total_elapsed=0.0):
        # silver panel + separator border
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (0, 0, HUD_WIDTH, self.height))
        pygame.draw.line(self.screen, COLOR_HUD_BORDER, (HUD_WIDTH, 0), (HUD_WIDTH, self.height), 2)

        # mode on top, most prominent
        pad_x = 14
        y = 16
        head_surf = self.font_header.render("MODE", True, COLOR_HEADER)
        self.screen.blit(head_surf, (pad_x, y))
        y += head_surf.get_height() + 2
        mode_surf = self.font_mode.render(self.solver_name, True, COLOR_TEXT)
        self.screen.blit(mode_surf, (pad_x, y))
        y += mode_surf.get_height() + 8
        pygame.draw.line(self.screen, COLOR_HUD_BORDER, (pad_x, y), (HUD_WIDTH - pad_x, y), 1)
        y += 14

        y = self._hud_section(y, "STEP", [f"{mouse.moves_count}"])
        y = self._hud_section(y, "TOTAL TIME (REAL)", [f"{total_elapsed:.3f} s"])
        y = self._hud_section(y, "COMPUTATION TIME (ALGO)",
                               [f"{mouse.total_computation_time * 1000:.2f} ms",
                                f"/ {self.max_computation_ms:.0f} ms"])
        y = self._hud_section(y, "HEADING",
                               [f"{mouse.heading}  {HEADING_ARROW[mouse.heading]}"])
        y = self._hud_section(y, "POSITION", [f"{mouse.position}"])

        if status_text:
            color = COLOR_WIN if "Success" in status_text else COLOR_DEAD
            pygame.draw.line(self.screen, COLOR_HUD_BORDER, (pad_x, y), (HUD_WIDTH - pad_x, y), 1)
            y += 10
            # explicit newlines mark intended line breaks; wrap only if a
            # single line is still too wide for the panel
            for part in status_text.split("\n"):
                for line in self._wrap_text(part, self.font_status, HUD_WIDTH - pad_x * 2):
                    status_surf = self.font_status.render(line, True, color)
                    self.screen.blit(status_surf, (pad_x, y))
                    y += status_surf.get_height() + 2

        self.draw_mouse_portrait(mouse)

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

    def wait_for_close(self):
        """Keep the final screen up until the user closes the window
        (X button) or presses Q."""
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                break
        pygame.quit()
