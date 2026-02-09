from typing import List, Tuple, Optional, Set
from collections import deque
import heapq

class Direction:
    """
    Класс направлений движения робота
    """
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (-1, 1)
    DOWN_LEFT = (1, -1)
    DOWN_RIGHT = (1, 1)

class RobotPathFinder:
    """Класс для поиска пути робота по матрице с точками"""
    
    def __init__(self, matrix: List[List[int]], 
                 obstacles: List[int] = None,
                 allow_diagonal: bool = False,
                 robot_size: int = 1):
        """
        Инициализация поиска пути для робота
        
        Args:
            matrix: матрица пространства
            obstacles: значения, которые считаются препятствиями
            allow_diagonal: разрешены ли диагональные движения
            robot_size: размер робота в клетках (1 = занимает 1 клетку)
        """
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if matrix else 0
        self.obstacles = set(obstacles) if obstacles else {1}
        self.allow_diagonal = allow_diagonal
        self.robot_size = robot_size
        
        # Сохраняем начальное состояние матрицы для отслеживания изменений
        self.initial_matrix = [row[:] for row in matrix]
        
        # Направления движения
        self.directions = [
            Direction.UP, Direction.DOWN, 
            Direction.LEFT, Direction.RIGHT
        ]
        if allow_diagonal:
            self.directions.extend([
                Direction.UP_LEFT, Direction.UP_RIGHT,
                Direction.DOWN_LEFT, Direction.DOWN_RIGHT
            ])
    
    def is_cell_free(self, row: int, col: int) -> bool:
        """
        Проверка, свободна ли клетка с учетом размера робота
        
        Args:
            row: Номер строки проверяемой клетки
            col: Номер столбца проверяемой клетки
            
        Returns:
            bool: True если клетка и все клетки, занимаемые роботом свободны, False в противном случае
        """
        # Проверяем все клетки, занимаемые роботом
        for dr in range(self.robot_size):
            for dc in range(self.robot_size):
                r, c = row + dr, col + dc
                if (r >= self.rows or c >= self.cols or 
                    self.matrix[r][c] in self.obstacles):
                    return False
        return True
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """
        Проверка валидности позиции для робота с учетом его размера
        
        Args:
            row: Номер строки проверяемой позиции
            col: Номер столбца проверяемой позиции
            
        Returns:
            bool: True если позиция валидна для робота, False в противном случае
        """
        return (0 <= row < self.rows - self.robot_size + 1 and 
                0 <= col < self.cols - self.robot_size + 1 and
                self.is_cell_free(row, col))
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Получение всех доступных соседних позиций с учетом разрешенных направлений движения
        
        Args:
            row: Номер строки текущей позиции
            col: Номер столбца текущей позиции
            
        Returns:
            List[Tuple[int, int]]: Список доступных соседних позиций (row, col)
        """
        neighbors = []
        for direction in self.directions:
            dr, dc = direction
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                neighbors.append((new_row, new_col))
        return neighbors
    
    def find_path_astar(self, start: Tuple[int, int],
                       end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Поиск пути с помощью алгоритма A* (A-star)
        Более эффективен для больших матриц по сравнению с BFS
        
        Args:
            start: Стартовая позиция (row, col)
            end: Конечная позиция (row, col)
            
        Returns:
            Optional[List[Tuple[int, int]]]: Список позиций от start до end или None если путь не найден
        """
        if not (self.is_valid_position(*start) and self.is_valid_position(*end)):
            return None
        
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            """Манхэттенское расстояние или евклидово для диагональных движений"""
            if self.allow_diagonal:
                # Евклидово расстояние
                return ((a[0] - b[0])**2 + (a[1] - b[1])**2) ** 0.5
            else:
                # Манхэттенское расстояние
                return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        open_set = []
        heapq.heappush(open_set, (0, 0, start, [start]))  # (f_score, g_score, position, path)
        
        g_scores = {start: 0}
        visited = set()
        
        while open_set:
            f_score, g_score, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in visited:
                continue
                
            visited.add(current_pos)
            
            if current_pos == end:
                return path
            
            for neighbor in self.get_neighbors(*current_pos):
                if neighbor in visited:
                    continue
                
                # Стоимость перехода (1 для ортогональных, sqrt(2) для диагональных)
                move_cost = 1.0
                if abs(neighbor[0] - current_pos[0]) + abs(neighbor[1] - current_pos[1]) == 2:
                    move_cost = 1.414  # sqrt(2) для диагональных движений
                
                new_g_score = g_score + move_cost
                
                if neighbor not in g_scores or new_g_score < g_scores[neighbor]:
                    g_scores[neighbor] = new_g_score
                    f_score = new_g_score + heuristic(neighbor, end)
                    new_path = path + [neighbor]
                    heapq.heappush(open_set, (f_score, new_g_score, neighbor, new_path))
        
        return None
    
    def find_path_through_points(self, points: List[Tuple[int, int]],
                                method: str = 'astar') -> Optional[List[Tuple[int, int]]]:
        """
        Поиск пути через несколько точек в заданном порядке
        
        Args:
            points: Список точек для посещения в порядке [p1, p2, p3, ...]
            method: Метод поиска ('bfs' или 'astar')
            
        Returns:
            Optional[List[Tuple[int, int]]]: Полный путь через все точки или None если путь не найден
        """
        if len(points) < 2:
            return points if points else None
        
        full_path = []
        current_point = points[0]
        
        for i in range(1, len(points)):
            next_point = points[i]
            
            # Выбираем метод поиска
            if method.lower() == 'bfs':
                segment_path = self.find_path_bfs(current_point, next_point)
            else:
                segment_path = self.find_path_astar(current_point, next_point)
            
            if segment_path is None:
                print(f"Не удалось найти путь от {current_point} до {next_point}")
                return None
            
            # Добавляем сегмент пути (без дублирования последней точки)
            full_path.extend(segment_path[:-1])
            current_point = next_point
        
        # Добавляем последнюю точку
        full_path.append(current_point)
        
        return full_path
    
    def visualize_path(self, path: List[Tuple[int, int]] = None,
                      points: List[Tuple[int, int]] = None) -> str:
        """
        Визуализация пути робота в матрице
        
        Args:
            path: Путь робота в виде списка позиций
            points: Список отмеченных точек
            
        Returns:
            str: Строковое представление визуализации пути
        """
        visualization = []
        
        for r in range(self.rows):
            row_str = []
            for c in range(self.cols):
                cell_value = self.matrix[r][c]
                
                # Проверяем, является ли клетка препятствием
                if cell_value in self.obstacles:
                    row_str.append('██')
                # Проверяем, является ли это точкой пути
                elif path and (r, c) in path:
                    idx = path.index((r, c))
                    if idx == 0:
                        row_str.append('S ')  # Старт
                    elif idx == len(path) - 1:
                        row_str.append('E ')  # Финиш
                    else:
                        # Определяем направление движения
                        prev = path[idx-1] if idx > 0 else (r, c)
                        next_pos = path[idx+1] if idx < len(path)-1 else (r, c)
                        
                        # Отображаем направление
                        if next_pos[0] < r: row_str.append('↑ ')
                        elif next_pos[0] > r: row_str.append('↓ ')
                        elif next_pos[1] < c: row_str.append('← ')
                        elif next_pos[1] > c: row_str.append('→ ')
                        else: row_str.append('· ')
                # Проверяем, является ли это отмеченной точкой
                elif points and (r, c) in points:
                    row_str.append('★ ')
                else:
                    row_str.append('. ')
            visualization.append(''.join(row_str))
        
        return '\n'.join(visualization)