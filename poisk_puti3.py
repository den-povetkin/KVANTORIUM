from typing import List, Tuple, Optional, Dict, Set
from collections import deque, defaultdict
import heapq
from enum import Enum


class Direction(Enum):
    """Направления движения робота"""
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
        """Проверка, свободна ли клетка (учитывает размер робота)"""
        # Проверяем все клетки, занимаемые роботом
        for dr in range(self.robot_size):
            for dc in range(self.robot_size):
                r, c = row + dr, col + dc
                if (r >= self.rows or c >= self.cols or 
                    self.matrix[r][c] in self.obstacles):
                    return False
        return True
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Проверка валидности позиции для робота"""
        return (0 <= row < self.rows - self.robot_size + 1 and 
                0 <= col < self.cols - self.robot_size + 1 and
                self.is_cell_free(row, col))
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Получение всех доступных соседних позиций"""
        neighbors = []
        for direction in self.directions:
            dr, dc = direction.value
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                neighbors.append((new_row, new_col))
        return neighbors
    
    def find_path_bfs(self, start: Tuple[int, int], 
                     end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Поиск кратчайшего пути с помощью BFS
        
        Args:
            start: стартовая позиция (row, col)
            end: конечная позиция (row, col)
            
        Returns:
            Список позиций от start до end или None если путь не найден
        """
        if not (self.is_valid_position(*start) and self.is_valid_position(*end)):
            return None
        
        queue = deque()
        queue.append((start, [start]))  # (position, path)
        visited = set([start])
        
        while queue:
            current_pos, path = queue.popleft()
            
            if current_pos == end:
                return path
            
            for neighbor in self.get_neighbors(*current_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        
        return None
    
    def find_path_astar(self, start: Tuple[int, int], 
                       end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Поиск пути с помощью алгоритма A*
        Более эффективен для больших матриц
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
            points: список точек для посещения в порядке [p1, p2, p3, ...]
            method: метод поиска ('bfs' или 'astar')
            
        Returns:
            Полный путь через все точки
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
    
    def optimize_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Упрощение пути - удаление промежуточных точек на прямой линии
        """
        if len(path) < 3:
            return path
        
        optimized = [path[0]]
        
        for i in range(1, len(path) - 1):
            prev = optimized[-1]
            curr = path[i]
            next_pos = path[i + 1]
            
            # Проверяем, лежат ли три точки на одной прямой
            if not self._are_points_collinear(prev, curr, next_pos):
                optimized.append(curr)
        
        optimized.append(path[-1])
        return optimized
    
    def _are_points_collinear(self, p1: Tuple[int, int], 
                            p2: Tuple[int, int], 
                            p3: Tuple[int, int]) -> bool:
        """Проверка, лежат ли три точки на одной прямой"""
        return (p2[0] - p1[0]) * (p3[1] - p2[1]) == (p3[0] - p2[0]) * (p2[1] - p1[1])
    
    def calculate_path_cost(self, path: List[Tuple[int, int]]) -> float:
        """Вычисление стоимости пути"""
        if len(path) < 2:
            return 0
        
        total_cost = 0
        for i in range(len(path) - 1):
            p1, p2 = path[i], path[i + 1]
            # Расстояние между точками
            dr, dc = abs(p2[0] - p1[0]), abs(p2[1] - p1[1])
            if dr == 1 and dc == 1:
                total_cost += 1.414  # Диагональное движение
            else:
                total_cost += 1.0  # Ортогональное движение
        
        return total_cost
    
    def visualize_path(self, path: List[Tuple[int, int]] = None,
                      points: List[Tuple[int, int]] = None) -> str:
        """Визуализация пути робота в матрице"""
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


# Пример использования
def main():
    # Пример матрицы среды (0 - свободно, 1 - препятствие)
    environment = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]
    
    print("=== Планирование пути для робота ===")
    print(f"Размер матрицы: {len(environment)}x{len(environment[0])}")
    
    # Создаем планировщик пути
    path_finder = RobotPathFinder(
        matrix=environment,
        obstacles=[1],
        allow_diagonal=True,
        robot_size=1
    )
    
    # Определяем точки для посещения
    points_to_visit = [(0, 0),(0,7),(7, 7)]
    
    print(f"\nТочки для посещения: {points_to_visit}")
    
    # Находим путь через все точки
    full_path = path_finder.find_path_through_points(
        points=points_to_visit,
        method='astar'
    )
    
    if full_path:
        # Оптимизируем путь
        optimized_path = path_finder.optimize_path(full_path)
        
        print(f"\n✅ Путь найден!")
        print(f"Длина полного пути: {len(full_path)} шагов")
        print(f"Длина оптимизированного пути: {len(optimized_path)} шагов")
        print(f"Стоимость пути: {path_finder.calculate_path_cost(full_path):.2f}")
        
        print("\nПолный путь:")
        for i, pos in enumerate(full_path):
            print(f"  Шаг {i:2d}: {pos}")
        
        print("\nОптимизированный путь:")
        for i, pos in enumerate(optimized_path):
            print(f"  Шаг {i:2d}: {pos}")
        
        # Визуализация
        print("\nВизуализация пути:")
        print(path_finder.visualize_path(path=full_path, points=points_to_visit))
'''        
        # Поиск пути между двумя точками
        print("\n=== Пример поиска между двумя точками ===")
        start_point = (0, 0)
        end_point = (7, 7)
        
        single_path = path_finder.find_path_astar(start_point, end_point)
        if single_path:
            print(f"Путь от {start_point} до {end_point}:")
            print(f"Длина: {len(single_path)} шагов")
            print(f"Стоимость: {path_finder.calculate_path_cost(single_path):.2f}")
            
            print("\nВизуализация:")
            print(path_finder.visualize_path(path=single_path))
    else:
        print("❌ Не удалось найти путь через все точки")

'''
if __name__ == "__main__":
    main()