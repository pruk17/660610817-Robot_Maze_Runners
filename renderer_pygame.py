"""
renderer_pygame.py
แสดงผลเขาวงกตแบบกราฟิก real-time ด้วย pygame (ข้อ 14: grid mode)
ขนาดช่องบนจอ (PIXELS_PER_CELL) เป็นการย่อส่วนจากขนาดจริง 16 cm/ช่อง
"""

import pygame

PIXELS_PER_CELL = 20   # ย่อส่วนจาก 16 cm จริง เป็น 20 px บนจอ
WALL_THICKNESS = 2
MARGIN = 20            # เผื่อขอบไว้แสดงข้อความสถานะ
HUD_HEIGHT = 60

COLOR_BG = (250, 248, 240)
COLOR_WALL = (40, 40, 40)
COLOR_MOUSE = (120, 70, 30)
COLOR_MOUSE_EYE = (255, 255, 255)
COLOR_CHEESE = (255, 196, 20)
COLOR_START = (180, 220, 255)
COLOR_TEXT = (20, 20, 20)
COLOR_DEAD = (200, 40, 40)
COLOR_WIN = (30, 160, 60)


class PygameRenderer:
    def __init__(self, maze):
        pygame.init()
        pygame.display.set_caption("Maze Mouse - หนูหาชีสในเขาวงกต")
        board_px = maze.size * PIXELS_PER_CELL
        self.width = board_px + MARGIN * 2
        self.height = board_px + MARGIN * 2 + HUD_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont("Tahoma", 18)
        self.font_small = pygame.font.SysFont("Tahoma", 14)
        self.clock = pygame.time.Clock()

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
        # จุดรูชีสเล็กๆ
        pygame.draw.circle(self.screen, COLOR_BG, (center[0] - 3, center[1] - 2), 2)
        pygame.draw.circle(self.screen, COLOR_BG, (center[0] + 2, center[1] + 3), 2)

    def draw_mouse(self, mouse):
        x, y = self.cell_to_px(*mouse.position)
        cx, cy = x + PIXELS_PER_CELL // 2, y + PIXELS_PER_CELL // 2
        radius = PIXELS_PER_CELL // 2 - 3
        pygame.draw.circle(self.screen, COLOR_MOUSE, (cx, cy), radius)

        # จมูก/ทิศทางที่หันหน้า แสดงเป็นจุดเล็กด้านหน้า
        offset = {"N": (0, -radius), "S": (0, radius), "E": (radius, 0), "W": (-radius, 0)}[mouse.heading]
        nose = (cx + offset[0], cy + offset[1])
        pygame.draw.circle(self.screen, COLOR_MOUSE_EYE, nose, 3)

    def draw_hud(self, mouse, status_text=""):
        y_base = self.height - HUD_HEIGHT
        pygame.draw.rect(self.screen, (235, 235, 225), (0, y_base, self.width, HUD_HEIGHT))
        info = (f"ก้าวที่: {mouse.moves_count}   "
                 f"เวลาคำนวณสะสม: {mouse.total_computation_time:.3f}s / 180s   "
                 f"หันหน้า: {mouse.heading}")
        text_surf = self.font_small.render(info, True, COLOR_TEXT)
        self.screen.blit(text_surf, (MARGIN, y_base + 6))

        if status_text:
            color = COLOR_WIN if "สำเร็จ" in status_text else COLOR_DEAD
            status_surf = self.font.render(status_text, True, color)
            self.screen.blit(status_surf, (MARGIN, y_base + 28))

    def render(self, maze, mouse, status_text=""):
        # เคลียร์ event queue กันโปรแกรมค้าง (ปิดหน้าต่างได้)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        self.screen.fill(COLOR_BG)
        self.draw_start_and_cheese(maze)
        self.draw_walls(maze)
        self.draw_mouse(mouse)
        self.draw_hud(mouse, status_text)
        pygame.display.flip()

    def save_screenshot(self, path):
        pygame.image.save(self.screen, path)

    def tick(self, fps=30):
        self.clock.tick(fps)

    def wait_and_close(self, seconds=3):
        pygame.time.wait(int(seconds * 1000))
        pygame.quit()
