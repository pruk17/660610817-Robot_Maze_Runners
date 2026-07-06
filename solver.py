"""
solver.py
FloodFillSolver: จำลอง "กลิ่นชีส" ที่หนูรู้สึกได้ในทุกช่อง (ค่าระยะทางไปชีสของแต่ละช่อง)
แต่หนูจะตัดสินใจ "การเคลื่อนไหวเดียว" ในแต่ละครั้งเท่านั้น (เลี้ยวซ้าย/ขวา/หน้า/หลัง)
ไม่มีการเก็บลำดับเส้นทางทั้งหมดไว้ล่วงหน้า (ข้อ 16) -- มีแค่ค่าสนามระยะทางต่อช่อง (เหมือนกลิ่น)
"""

from collections import deque

from maze_model import Maze
from agent import CLOCKWISE


class FloodFillSolver:
    def __init__(self, maze: Maze):
        # คำนวณ "สนามกลิ่น" (distance field) จาก exit ไปทุกช่องหนึ่งครั้งตอนเริ่มเกม
        # นี่คือสิ่งที่แทน "หนูได้กลิ่นชีส/รู้ว่าชีสอยู่ตรงไหน" (ข้อ 12)
        # แต่ไม่ใช่ path สำเร็จรูป หนูยังต้องตัดสินใจเองทีละก้าวจากค่านี้
        self.distance_field = self._build_distance_field(maze)

    def _build_distance_field(self, maze: Maze):
        size = maze.size
        dist = [[None] * size for _ in range(size)]
        goal = maze.exit
        dist[goal[0]][goal[1]] = 0
        queue = deque([goal])
        while queue:
            r, c = queue.popleft()
            for d in maze.neighbors_open((r, c)):
                dr, dc = Maze.DELTA[d]
                nr, nc = r + dr, c + dc
                if dist[nr][nc] is None:
                    dist[nr][nc] = dist[r][c] + 1
                    queue.append((nr, nc))
        return dist

    def decide_next_action(self, mouse, maze: Maze) -> str:
        """
        ตัดสินใจ action เดียวสำหรับการเคลื่อนไหวครั้งนี้ครั้งเดียวเท่านั้น
        โดยดูค่าระยะทาง (กลิ่น) ของช่องข้างเคียงที่เดินได้จริง แล้วเลือกทิศที่ใกล้ชีสที่สุด
        ถ้าทิศนั้นไม่ตรงกับ heading ปัจจุบัน ต้องเลี้ยวก่อน (1 การเคลื่อนไหว = เลี้ยวได้แค่ครั้งเดียว)
        """
        r, c = mouse.position
        current_dist = self.distance_field[r][c]

        best_dir = None
        best_dist = current_dist
        for d in maze.neighbors_open((r, c)):
            dr, dc = Maze.DELTA[d]
            nr, nc = r + dr, c + dc
            nd = self.distance_field[nr][nc]
            if nd < best_dist:
                best_dist = nd
                best_dir = d

        if best_dir is None:
            # ไม่ควรเกิดขึ้นในเขาวงกตที่เชื่อมกันหมด (ยกเว้นถึงเป้าหมายแล้ว)
            return "FORWARD"

        if best_dir == mouse.heading:
            return "FORWARD"
        if best_dir == mouse.opposite_heading():
            return "BACKWARD"

        # ต้องเลี้ยว -- เลือกว่าจะซ้ายหรือขวา (เลี้ยวได้ทีละ 1 ครั้งต่อ 1 การเคลื่อนไหว)
        idx_current = CLOCKWISE.index(mouse.heading)
        idx_target = CLOCKWISE.index(best_dir)
        diff = (idx_target - idx_current) % 4
        return "TURN_RIGHT" if diff == 1 else "TURN_LEFT"
