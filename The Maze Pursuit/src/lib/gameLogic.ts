export type Position = { x: number; y: number };
export type CellType = 'wall' | 'floor' | 'exit';
export type ItemType = 'cheese' | 'bell' | null;

export type GameState = {
  maze: CellType[][];
  items: ItemType[][];
  jerry: { pos: Position; sight: number; mpTracker: number; cheeseTurnsLeft: number };
  tom: { pos: Position; sight: number; state: 'patrol' | 'chase' | 'search'; lastKnownJerryPos: Position | null; patrolTarget: Position | null };
  turn: number;
  status: 'playing' | 'jerry_won' | 'tom_won';
  traces: { pos: Position; age: number; agent: 'tom' | 'jerry' }[];
  jerryPath: Position[]; // Path assigned by clicking
  tomPath: Position[];  // Visualization for Dev Mode
  jerryMpBase: number;
  tomMpBase: number;
  isDeveloperMode: boolean;
};

export function generateRandomMaze(width: number, height: number): { maze: CellType[][], items: ItemType[][], jerryPos: Position, tomPos: Position, exitPos: Position } {
  const maze: CellType[][] = Array(height).fill(null).map(() => Array(width).fill('wall'));
  const items: ItemType[][] = Array(height).fill(null).map(() => Array(width).fill(null));

  // Randomized Prim's Algorithm
  const startX = 1;
  const startY = 1;
  maze[startY][startX] = 'floor';
  
  const walls: { x: number, y: number, nx: number, ny: number }[] = [];
  const addWalls = (cx: number, cy: number) => {
    const dirs = [
      { dx: 0, dy: -2 },
      { dx: 0, dy: 2 },
      { dx: -2, dy: 0 },
      { dx: 2, dy: 0 },
    ];
    for (const dir of dirs) {
      const nx = cx + dir.dx;
      const ny = cy + dir.dy;
      if (nx > 0 && ny > 0 && nx < width - 1 && ny < height - 1 && maze[ny][nx] === 'wall') {
        walls.push({ x: cx + dir.dx / 2, y: cy + dir.dy / 2, nx, ny });
      }
    }
  };
  
  addWalls(startX, startY);

  while (walls.length > 0) {
    const idx = Math.floor(Math.random() * walls.length);
    const wall = walls[idx];
    walls.splice(idx, 1);

    if (maze[wall.ny][wall.nx] === 'wall') {
      maze[wall.y][wall.x] = 'floor'; // Break wall
      maze[wall.ny][wall.nx] = 'floor'; // Carve target 
      addWalls(wall.nx, wall.ny);
    }
  }

  // Remove some random walls to create loops
  // Ensure we don't create 2x2 open spaces
  const canRemoveWall = (x: number, y: number) => {
    if (maze[y-1][x-1] === 'floor' && maze[y-1][x] === 'floor' && maze[y][x-1] === 'floor') return false;
    if (maze[y-1][x] === 'floor' && maze[y-1][x+1] === 'floor' && maze[y][x+1] === 'floor') return false;
    if (maze[y][x-1] === 'floor' && maze[y+1][x-1] === 'floor' && maze[y+1][x] === 'floor') return false;
    if (maze[y][x+1] === 'floor' && maze[y+1][x] === 'floor' && maze[y+1][x+1] === 'floor') return false;
    return true;
  };

  const loopsCount = Math.floor((width * height) / 30);
  let removed = 0;
  for (let i = 0; i < (width * height) * 5 && removed < loopsCount; i++) {
    const x = Math.floor(Math.random() * (width - 2)) + 1;
    const y = Math.floor(Math.random() * (height - 2)) + 1;
    if (maze[y][x] === 'wall') {
        let floorNeighbors = 0;
        if (maze[y-1][x] === 'floor') floorNeighbors++;
        if (maze[y+1][x] === 'floor') floorNeighbors++;
        if (maze[y][x-1] === 'floor') floorNeighbors++;
        if (maze[y][x+1] === 'floor') floorNeighbors++;
        if (floorNeighbors >= 2 && canRemoveWall(x, y)) {
           maze[y][x] = 'floor';
           removed++;
        }
    }
  }

  const floors: Position[] = [];
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      if (maze[y][x] === 'floor') floors.push({ x, y });
    }
  }

  const jerryPos = { x: 1, y: 1 };
  
  const edgeFloors = floors.filter(p => p.x === 1 || p.x === width - 2 || p.y === 1 || p.y === height - 2);
  edgeFloors.sort((a, b) => {
      return (Math.abs(b.x - jerryPos.x) + Math.abs(b.y - jerryPos.y)) - (Math.abs(a.x - jerryPos.x) + Math.abs(a.y - jerryPos.y));
  });
  
  // Pick a random exit from the top 25% furthest edge tiles
  const exitCandidates = edgeFloors.slice(0, Math.max(1, Math.floor(edgeFloors.length * 0.25)));
  const exitPos = exitCandidates[Math.floor(Math.random() * exitCandidates.length)];
  maze[exitPos.y][exitPos.x] = 'exit';
  
  // Sort all floors for item/Tom placement
  floors.sort((a, b) => {
      return (Math.abs(b.x - jerryPos.x) + Math.abs(b.y - jerryPos.y)) - (Math.abs(a.x - jerryPos.x) + Math.abs(a.y - jerryPos.y));
  });

  // Spawn Tom reasonably far, but not literally at the exit tile.
  const tomPos = floors[Math.floor(floors.length * 0.15)];
  
  // Multiple Cheese placement
  const cheeseCount = 4;
  for (let i = 0; i < cheeseCount; i++) {
    const idx = Math.floor(floors.length * (0.3 + (i * 0.15)));
    const pos = floors[idx % floors.length];
    if (maze[pos.y][pos.x] === 'floor' && items[pos.y][pos.x] === null) {
      items[pos.y][pos.x] = 'cheese';
    }
  }

  const bellPos = floors[Math.floor(floors.length / 3)];
  items[bellPos.y][bellPos.x] = 'bell';

  return { maze, items, jerryPos, tomPos, exitPos };
}

export function createInitialState(): GameState {
  const { maze, items, jerryPos, tomPos } = generateRandomMaze(21, 15);

  return {
    maze,
    items,
    jerry: { pos: jerryPos, sight: 4, mpTracker: 2, cheeseTurnsLeft: 0 },
    tom: { pos: tomPos, sight: 5, state: 'patrol', lastKnownJerryPos: null, patrolTarget: null },
    turn: 1,
    status: 'playing',
    traces: [],
    jerryPath: [],
    tomPath: [],
    jerryMpBase: 2, // Jerry has 2 MP normally
    tomMpBase: 2,   // Tom has 2 MP
    isDeveloperMode: false,
  };
}

export function manhattanDistance(p1: Position, p2: Position) {
  return Math.abs(p1.x - p2.x) + Math.abs(p1.y - p2.y);
}

export function getValidNeighbors(pos: Position, maze: CellType[][]): Position[] {
  const neighbors: Position[] = [];
  const dirs = [{ x: 0, y: -1 }, { x: 0, y: 1 }, { x: -1, y: 0 }, { x: 1, y: 0 }];
  for (const dir of dirs) {
    const nx = pos.x + dir.x;
    const ny = pos.y + dir.y;
    if (ny >= 0 && ny < maze.length && nx >= 0 && nx < maze[0].length && maze[ny][nx] !== 'wall') {
      neighbors.push({ x: nx, y: ny });
    }
  }
  return neighbors;
}

export function getBFSPath(start: Position, end: Position, maze: CellType[][]): Position[] {
  const queue: { pos: Position; path: Position[] }[] = [{ pos: start, path: [] }];
  const visited = new Set<string>();
  visited.add(`${start.x},${start.y}`);

  while (queue.length > 0) {
    const { pos, path } = queue.shift()!;
    if (pos.x === end.x && pos.y === end.y) return path;

    for (const neighbor of getValidNeighbors(pos, maze)) {
      const key = `${neighbor.x},${neighbor.y}`;
      if (!visited.has(key)) {
        visited.add(key);
        queue.push({ pos: neighbor, path: [...path, neighbor] });
      }
    }
  }
  return []; // No path found
}

// Raycasting / Bresenham's Line Algorithm for Line of Sight
export function getLineOfSight(x0: number, y0: number, x1: number, y1: number, maze: CellType[][]): boolean {
  let dx = Math.abs(x1 - x0);
  let dy = Math.abs(y1 - y0);
  let sx = x0 < x1 ? 1 : -1;
  let sy = y0 < y1 ? 1 : -1;
  let err = dx - dy;

  while (true) {
    if (x0 === x1 && y0 === y1) return true;
    if (maze[y0][x0] === 'wall') return false;
    let e2 = 2 * err;
    if (e2 > -dy) { err -= dy; x0 += sx; }
    if (e2 < dx) { err += dx; y0 += sy; }
  }
}

export function getVisibleCells(pos: Position, radius: number, maze: CellType[][]): Set<string> {
  const visible = new Set<string>();
  for (let y = 0; y < maze.length; y++) {
    for (let x = 0; x < maze[0].length; x++) {
      const dist = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
      if (dist <= radius + 0.5) {
        if (getLineOfSight(pos.x, pos.y, x, y, maze)) {
          visible.add(`${x},${y}`);
        }
      }
    }
  }
  return visible;
}

// Minimax with Alpha-Beta Pruning for Tom
export function getMinimaxMove(tomPos: Position, jerryPos: Position, maze: CellType[][]): Position | null {
  const depth = 3;
  let bestScore = -Infinity;
  let bestMove: Position | null = null;
  const moves = getValidNeighbors(tomPos, maze);

  for (const move of moves) {
    const score = minimax(move, jerryPos, depth - 1, -Infinity, Infinity, false, maze);
    if (score > bestScore) {
      bestScore = score;
      bestMove = move;
    }
  }
  
  // If no optimal move found strictly better, fallback to a safe forward progress, or random valid move
  if (!bestMove && moves.length > 0) {
      return moves[0];
  }
  return bestMove;
}

function minimax(
  tomPos: Position,
  jerryPos: Position,
  depth: number,
  alpha: number,
  beta: number,
  isMaximizingTom: boolean,
  maze: CellType[][]
): number {
  if (depth === 0 || (tomPos.x === jerryPos.x && tomPos.y === jerryPos.y)) {
    // Distance Metric
    const dist = manhattanDistance(tomPos, jerryPos);
    // Safety Factor for Jerry (Evaluate available exits)
    const jerryExits = getValidNeighbors(jerryPos, maze).length;
    // Tom wants to MAXIMIZE score. Thus negative distance is better for Tom.
    // Jerry with fewer exits is better for Tom.
    return -dist - jerryExits;
  }

  if (isMaximizingTom) {
    let maxEval = -Infinity;
    for (const m of getValidNeighbors(tomPos, maze)) {
      const score = minimax(m, jerryPos, depth - 1, alpha, beta, false, maze);
      maxEval = Math.max(maxEval, score);
      alpha = Math.max(alpha, score);
      if (beta <= alpha) break; // Alpha-beta pruning
    }
    return maxEval === -Infinity ? -100 : maxEval; // Penalty if trapped
  } else {
    // Jerry minimizing Tom's score
    let minEval = Infinity;
    for (const m of getValidNeighbors(jerryPos, maze)) {
      const score = minimax(tomPos, m, depth - 1, alpha, beta, true, maze);
      minEval = Math.min(minEval, score);
      beta = Math.min(beta, score);
      if (beta <= alpha) break; // Alpha-beta pruning
    }
    return minEval === Infinity ? 100 : minEval; // Reward Jerry if trapped? Wait, if minEval is Infinity, means Jerry is trapped. It's good for Tom (Max).
  }
}
