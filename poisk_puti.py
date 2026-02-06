from collections import deque
from typing import List, Tuple, Optional

def find_path_in_matrix(matrix: List[List[int]], start: Tuple[int, int], 
                        end: Tuple[int, int], obstacle: int = 1) -> Optional[List[Tuple[int, int]]]:
    """
    Поиск кратчайшего пути от start до end в матрице.
    obstacle - значение, обозначающее препятствие.
    
    matrix = [
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 0, 0]
    ]
    start = (0, 0)
    end = (3, 3)
    """
    if not matrix or not matrix[0]:
        return None
    
    rows, cols = len(matrix), len(matrix[0])
    
    # Проверка координат
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return None
    if not (0 <= end[0] < rows and 0 <= end[1] < cols):
        return None
    
    # Если старт или цель - препятствие
    if matrix[start[0]][start[1]] == obstacle or matrix[end[0]][end[1]] == obstacle:
        return None
    
    # Направления движения (вверх, вниз, влево, вправо)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # Очередь для BFS: (row, col, path)
    queue = deque([(start[0], start[1], [start])])
    visited = set([start])
    
    while queue:
        row, col, path = queue.popleft()
        
        # Если достигли цели
        if (row, col) == end:
            return path
        
        # Исследуем соседние клетки
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if (0 <= new_row < rows and 0 <= new_col < cols and
                matrix[new_row][new_col] != obstacle and
                (new_row, new_col) not in visited):
                
                new_path = path + [(new_row, new_col)]
                queue.append((new_row, new_col, new_path))
                visited.add((new_row, new_col))
    
    return None  # Путь не найден


# Пример использования
if __name__ == "__main__":
    # Пример матрицы (0 - свободно, 1 - препятствие)
    matrix = [
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 0, 0]
    ]
    
    start = (0, 2)
    end = (3, 3)
    
    path = find_path_in_matrix(matrix, start, end)
    
    if path:
        print("Путь найден:")
        for point in path:
            print(f"  {point}")
        print(f"Длина пути: {len(path)-1} шагов")
    else:
        print("Путь не найден")