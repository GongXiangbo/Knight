# Knight Path Finder

Finds all shortest paths for a knight on a chessboard between two positions.

## Features

- Algebraic chess notation support
- Multiple output formats (PDF, JPG, DOT)
- Configuration file support
- Docker support
- Logging
- Command line parameters

## Usage

### Using Docker Compose (recommended)

```bash
docker-compose up
```

### Using Docker

```bash
docker build -t knight-path .
docker run -v ./output:/app/output knight-path --start a1 --end h8
```

### Direct Python Usage

```bash
pip install -r requirements.txt
python knight.py --start a1 --end h8
```

## Configuration

Edit `config.jsonc` to change default settings:
- Board size
- Default start/end positions
- Graph visualization settings

## Output

The program generates:
- JPG visualization
- DOT file
- Log file

## Command Line Arguments

- `--config`: Path to config file (default: config.jsonc)
- `--start`: Start position in algebraic notation (e.g., "a1")
- `--end`: End position in algebraic notation (e.g., "h8")
- `--output`: Output directory (default: output)
