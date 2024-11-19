import argparse
import json
import logging
from collections import defaultdict, deque
from pathlib import Path
import graphviz

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
        file, rank = alg[0], alg[1]
        y = ord(file) - 97
        x = self.size - int(rank)
        return (x, y)

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

def main():
    parser = argparse.ArgumentParser(description='Find shortest knight paths on a chessboard')
    parser.add_argument('--config', type=str, default='config.jsonc', help='Path to config file')
    parser.add_argument('--start', type=str, help='Start position (e.g. "a1")')
    parser.add_argument('--end', type=str, help='End position (e.g. "h8")')
    parser.add_argument('--output', type=str, default='output', help='Output directory')
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            # Remove any trailing commas that might exist in the config file
            content = f.read()
            # Simple cleanup of common JSONC elements
            cleaned_content = '\n'.join(line for line in content.split('\n') 
                                      if not line.strip().startswith('//'))
            config = json.loads(cleaned_content)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    board = ChessBoard(config.get('board_size', 8))
    
    start_pos = args.start or config.get('start_position')
    end_pos = args.end or config.get('end_position')
    
    if not start_pos or not end_pos:
        logger.error("Start and end positions must be provided")
        return

    try:
        start = board.algebraic_to_pos(start_pos)
        end = board.algebraic_to_pos(end_pos)
    except Exception as e:
        logger.error(f"Invalid position format: {e}")
        return

    logger.info(f"Finding paths from {start_pos} to {end_pos}")
    paths = find_all_shortest_paths(board, start, end)
    
    if not paths:
        logger.error("No valid paths found")
        return

    logger.info(f"Found {len(paths)} shortest paths")
    
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    dot = create_graph(board, paths)
    dot.render(str(output_dir / 'knight_paths'), format='pdf', cleanup=True)
    dot.render(str(output_dir / 'knight_paths'), format='jpg', cleanup=True)
    dot.save(str(output_dir / 'knight_paths.dot'))

    with open(output_dir / 'paths.txt', 'w') as f:
        for path in paths:
            algebraic_path = [board.pos_to_algebraic(pos) for pos in path]
            f.write(' -> '.join(algebraic_path) + '\n')

if __name__ == '__main__':
    main()
