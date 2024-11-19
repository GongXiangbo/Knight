import argparse
import json
import logging
import sys
from collections import defaultdict, deque
from pathlib import Path
import graphviz
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knight_paths.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChessBoard:
    def __init__(self, size=8):
        self.size = size
        
    def valid_moves(self, pos):
        x, y = pos
        moves = [
            (x+2, y+1), (x+2, y-1), (x-2, y+1), (x-2, y-1),
            (x+1, y+2), (x+1, y-2), (x-1, y+2), (x-1, y-2)
        ]
        return [(x, y) for x, y in moves if 0 <= x < self.size and 0 <= y < self.size]

    def pos_to_algebraic(self, pos):
        x, y = pos
        return f"{chr(97 + y)}{self.size - x}"
    
    def algebraic_to_pos(self, alg):
        if not re.match(r'^[a-h][1-8]$', alg):
            raise ValueError(f"Invalid algebraic notation: {alg}. Must be like 'a1', 'h8', etc.")
        file, rank = alg[0], alg[1]
        y = ord(file) - 97
        x = self.size - int(rank)
        return (x, y)

def get_user_input(prompt, validator=None, error_msg=None):
    while True:
        value = input(prompt).strip()
        if validator is None or validator(value):
            return value
        print(error_msg or "Invalid input. Please try again.")

def is_valid_position(pos):
    return bool(re.match(r'^[a-h][1-8]$', pos))

def find_all_shortest_paths(board, start, end):
    queue = deque([(start, [start])])
    paths = []
    seen = {start}
    layer = {start: 0}
    parent = defaultdict(list)
    
    while queue:
        vertex, path = queue.popleft()
        if vertex == end:
            paths.append(path)
        else:
            for next_pos in board.valid_moves(vertex):
                if next_pos not in layer:
                    layer[next_pos] = layer[vertex] + 1
                    parent[next_pos].append(vertex)
                    queue.append((next_pos, path + [next_pos]))
                    seen.add(next_pos)
                elif layer[next_pos] == layer[vertex] + 1:
                    parent[next_pos].append(vertex)

    return paths

def create_graph(board, paths):
    dot = graphviz.Digraph(comment='Knight Paths')
    dot.attr(rankdir='LR')
    
    nodes = set()
    edges = set()
    
    for path in paths:
        for i in range(len(path) - 1):
            src = board.pos_to_algebraic(path[i])
            dst = board.pos_to_algebraic(path[i + 1])
            nodes.add(src)
            nodes.add(dst)
            edges.add((src, dst))
    
    for node in nodes:
        dot.node(node)
    for src, dst in edges:
        dot.edge(src, dst)
    
    return dot

def show_menu():
    print("\nKnight Path Finder")
    print("=================")
    print("Please input positions in algebraic notation (e.g., 'a1', 'h8')")
    print("Press Ctrl+C at any time to exit")
    print()

def main():
    try:
        with open('config.jsonc') as f:
            content = f.read()
            cleaned_content = '\n'.join(line for line in content.split('\n') 
                                      if not line.strip().startswith('//'))
            config = json.loads(cleaned_content)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    board = ChessBoard(config.get('board_size', 8))
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    try:
        while True:
            show_menu()
            
            start_pos = get_user_input(
                "Enter start position (e.g., a1): ",
                validator=is_valid_position,
                error_msg="Invalid position. Please use format like 'a1', 'h8', etc."
            )
            
            end_pos = get_user_input(
                "Enter end position (e.g., h8): ",
                validator=is_valid_position,
                error_msg="Invalid position. Please use format like 'a1', 'h8', etc."
            )

            try:
                start = board.algebraic_to_pos(start_pos)
                end = board.algebraic_to_pos(end_pos)
            except ValueError as e:
                logger.error(str(e))
                continue

            logger.info(f"Finding paths from {start_pos} to {end_pos}")
            paths = find_all_shortest_paths(board, start, end)
            
            if not paths:
                print("\nNo valid paths found!")
                continue

            print(f"\nFound {len(paths)} shortest paths!")
            
            dot = create_graph(board, paths)
            dot.render(str(output_dir / 'knight_paths'), format='pdf', cleanup=True)
            dot.render(str(output_dir / 'knight_paths'), format='jpg', cleanup=True)
            dot.save(str(output_dir / 'knight_paths.dot'))

            with open(output_dir / 'paths.txt', 'w') as f:
                for path in paths:
                    algebraic_path = [board.pos_to_algebraic(pos) for pos in path]
                    path_str = ' -> '.join(algebraic_path)
                    f.write(path_str + '\n')
                    print(path_str)

            print("\nOutput files have been generated in the 'output' directory:")
            print("- knight_paths.pdf  (Graph visualization)")
            print("- knight_paths.jpg  (Graph visualization)")
            print("- knight_paths.dot  (Graphviz source)")
            print("- paths.txt         (Text list of all paths)")
            
            if get_user_input("\nCalculate another path? (y/n): ").lower() != 'y':
                break

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == '__main__':
    main()
