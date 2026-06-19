import React, { useState, useEffect, useRef } from 'react';
import {
  GameState,
  Position,
  createInitialState,
  getVisibleCells,
  getBFSPath,
  getMinimaxMove,
  getValidNeighbors,
  CellType,
} from '../lib/gameLogic';
import { Cat, Mouse, DoorOpen, Bell, Coins, RefreshCcw, Play, AudioWaveform } from 'lucide-react';

export default function GameBoard() {
  const [state, setState] = useState<GameState>(createInitialState());
  const jerryTarget = state.jerryPath.length > 0 ? state.jerryPath[state.jerryPath.length - 1] : null;

  // Derive visible set
  const visibleJerrySet = getVisibleCells(state.jerry.pos, state.jerry.sight, state.maze);
  
  // Developer Mode overrides
  const isDev = state.isDeveloperMode;
  
  // Audio indicator logic 
  const tomDistance = Math.abs(state.tom.pos.x - state.jerry.pos.x) + Math.abs(state.tom.pos.y - state.jerry.pos.y);
  const showSoundIndicator = tomDistance > 0 && tomDistance <= state.jerry.sight + 2 && !visibleJerrySet.has(`${state.tom.pos.x},${state.tom.pos.y}`);

  const handleCellClick = (x: number, y: number) => {
    if (state.status !== 'playing') return;
    if (state.maze[y][x] === 'wall') return;
    
    // Check if the cell is visible to Jerry. Fog of War constraint.
    // If we want Player to only move to visible cells:
    if (!visibleJerrySet.has(`${x},${y}`)) return;

    if (x === state.jerry.pos.x && y === state.jerry.pos.y) return;

    const path = getBFSPath(state.jerry.pos, { x, y }, state.maze);
    setState(s => {
      const newState = { ...s, jerryPath: path };
      // Also update tom's planned path for visualization if in dev mode
      if (s.isDeveloperMode) {
        let tp: Position[] = [];
        if (s.tom.state === 'chase') {
          tp = getBFSPath(s.tom.pos, s.jerry.pos, s.maze);
        } else if (s.tom.lastKnownJerryPos) {
          tp = getBFSPath(s.tom.pos, s.tom.lastKnownJerryPos, s.maze);
        } else if (s.tom.patrolTarget) {
          tp = getBFSPath(s.tom.pos, s.tom.patrolTarget, s.maze);
        }
        newState.tomPath = tp;
      }
      return newState;
    });
  };

  useEffect(() => {
    if (state.status !== 'playing') return;

    const tickInterval = setInterval(() => {
      setState(s => {
        // Create strict immutable copies
        const newState = {
          ...s,
          jerry: { ...s.jerry, pos: { ...s.jerry.pos } },
          tom: { ...s.tom, pos: { ...s.tom.pos }, patrolTarget: s.tom.patrolTarget ? { ...s.tom.patrolTarget } : null },
          jerryPath: [...s.jerryPath],
          tomPath: [...s.tomPath],
          traces: s.traces.map(t => ({ ...t, pos: { ...t.pos } })),
          items: s.items.map(row => [...row])
        };

        // --- JERRY'S ACTION ---
        let jerryMovedThisTick = false;
        if (newState.jerryPath.length > 0 && newState.jerry.mpTracker > 0) {
          const nextPos = newState.jerryPath.shift()!;
          newState.traces.push({ pos: newState.jerry.pos, age: 3, agent: 'jerry' }); // Add trace
          newState.jerry.pos = nextPos;
          newState.jerry.mpTracker -= 1;
          jerryMovedThisTick = true;

          // Pickup Items
          if (newState.items[nextPos.y][nextPos.x] === 'cheese') {
            newState.jerry.cheeseTurnsLeft = 5;
            newState.items[nextPos.y][nextPos.x] = null;
          }

          // Check End Conditions early
          if (newState.maze[nextPos.y][nextPos.x] === 'exit') {
            newState.status = 'jerry_won';
            return newState;
          }
          if (nextPos.x === newState.tom.pos.x && nextPos.y === newState.tom.pos.y) {
            newState.status = 'tom_won';
            return newState;
          }
        }

        // --- TOM'S TURN ---
        if (!jerryMovedThisTick && newState.jerry.mpTracker === 0) {
          // Global Scan Logic (Tom knows where Jerry is every 7 turns)
          const isScanning = newState.turn % 7 === 0;
          if (isScanning) {
            newState.tom.lastKnownJerryPos = { ...newState.jerry.pos };
            newState.tom.state = 'search';
          }

          // Process Tom's FSM & Move
          let tomMoves = newState.tomMpBase;
          for(let i=0; i<tomMoves; i++) {
            // FSM Check
            const tomVisible = getVisibleCells(newState.tom.pos, newState.tom.sight, newState.maze);
            const canSeeJerry = tomVisible.has(`${newState.jerry.pos.x},${newState.jerry.pos.y}`);
            
            // Hearing check: If Jerry is within 7 tiles, Tom "hears" him
            const distToJerry = Math.abs(newState.tom.pos.x - newState.jerry.pos.x) + Math.abs(newState.tom.pos.y - newState.jerry.pos.y);
            const canHearJerry = distToJerry <= 7;

            if (canSeeJerry) {
              newState.tom.state = 'chase';
              newState.tom.lastKnownJerryPos = { ...newState.jerry.pos };
            } else if (canHearJerry) {
              // If Tom can hear Jerry but not see him, he moves to the sound
              if (newState.tom.state !== 'chase') newState.tom.state = 'search';
              newState.tom.lastKnownJerryPos = { ...newState.jerry.pos };
            } else if (newState.tom.state === 'chase') {
              // Transition from CHASE to SEARCH: move to last known pos
              newState.tom.state = 'search';
            }

            // Power-up check
            if (newState.items[newState.tom.pos.y][newState.tom.pos.x] === 'bell') {
               newState.tom.sight = 7;
               newState.items[newState.tom.pos.y][newState.tom.pos.x] = null;
            }

            let nextTomPos: Position | null = null;
            if (canSeeJerry) {
              nextTomPos = getMinimaxMove(newState.tom.pos, newState.jerry.pos, newState.maze);
            } else if (newState.tom.state === 'search' && newState.tom.lastKnownJerryPos) {
              // Move to last known position
              if (newState.tom.pos.x === newState.tom.lastKnownJerryPos.x && newState.tom.pos.y === newState.tom.lastKnownJerryPos.y) {
                newState.tom.lastKnownJerryPos = null;
                newState.tom.state = 'patrol';
              } else {
                const path = getBFSPath(newState.tom.pos, newState.tom.lastKnownJerryPos, newState.maze);
                if (path && path.length > 0) {
                  nextTomPos = path[0];
                } else {
                  newState.tom.lastKnownJerryPos = null;
                  newState.tom.state = 'patrol';
                }
              }
            }
            
            if ((newState.tom.state === 'patrol' && !canHearJerry) || !nextTomPos) {
                if (!newState.tom.patrolTarget || (newState.tom.patrolTarget.x === newState.tom.pos.x && newState.tom.patrolTarget.y === newState.tom.pos.y)) {
                    const validCells: Position[] = [];
                    for(let y=0; y<newState.maze.length; y++) {
                        for(let x=0; x<newState.maze[y].length; x++) {
                           if(newState.maze[y][x] !== 'wall') validCells.push({x, y});
                        }
                    }
                    if(validCells.length > 0) {
                        newState.tom.patrolTarget = validCells[Math.floor(Math.random() * validCells.length)];
                    }
                }
                
                if (newState.tom.patrolTarget) {
                    const path = getBFSPath(newState.tom.pos, newState.tom.patrolTarget, newState.maze);
                    if (path && path.length > 0) {
                        nextTomPos = path[0];
                    } else {
                        newState.tom.patrolTarget = null;
                        const neighbors = getValidNeighbors(newState.tom.pos, newState.maze);
                        if (neighbors.length > 0) nextTomPos = neighbors[Math.floor(Math.random() * neighbors.length)];
                    }
                } else {
                   const neighbors = getValidNeighbors(newState.tom.pos, newState.maze);
                   if (neighbors.length > 0) nextTomPos = neighbors[Math.floor(Math.random() * neighbors.length)];
                }
            }

            if (nextTomPos) {
              newState.traces.push({ pos: newState.tom.pos, age: 3, agent: 'tom' }); // Add trace
              newState.tom.pos = nextTomPos;
              
              // Update tom path for visualization
              if (newState.isDeveloperMode) {
                if (newState.tom.state === 'chase') {
                  newState.tomPath = getBFSPath(newState.tom.pos, newState.jerry.pos, newState.maze);
                } else if (newState.tom.lastKnownJerryPos) {
                  newState.tomPath = getBFSPath(newState.tom.pos, newState.tom.lastKnownJerryPos, newState.maze);
                } else if (newState.tom.patrolTarget) {
                  newState.tomPath = getBFSPath(newState.tom.pos, newState.tom.patrolTarget, newState.maze);
                }
              }

              if (nextTomPos.x === newState.jerry.pos.x && nextTomPos.y === newState.jerry.pos.y) {
                newState.status = 'tom_won';
                return newState;
              }
            }
          }

          // Clean up traces
          newState.traces = newState.traces.map(t => ({ ...t, age: t.age - 1 })).filter(t => t.age > 0);

          // Reset Turn & MP
          newState.turn += 1;
          
          if (newState.jerry.cheeseTurnsLeft > 0) {
             newState.jerry.cheeseTurnsLeft -= 1;
             newState.jerry.mpTracker = newState.jerryMpBase + 1; // Faster while powerup active
          } else {
             newState.jerry.mpTracker = newState.jerryMpBase;
          }
        }

        return newState;
      });
    }, 250);

    return () => clearInterval(tickInterval);
  }, [state.status]);

  const onRestart = () => {
    setState(createInitialState());
  }

  const toggleDevMode = () => {
    setState(s => ({ ...s, isDeveloperMode: !s.isDeveloperMode }));
  }

  return (
    <div className="min-h-screen bg-indigo-950 text-white flex flex-col font-sans select-none sm:py-6 sm:px-4 sm:items-center">
      <div className="max-w-[1024px] w-full flex flex-col gap-6 flex-1 drop-shadow-2xl">
      
        {/* HEADER */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center p-6 md:h-24 bg-indigo-900 md:rounded-3xl border-b-4 md:border-4 border-indigo-800 shadow-xl gap-4 shrink-0 transition-all">
          <div className="flex items-center space-x-6">
            <div className="bg-yellow-400 p-2 rounded-xl shadow-[0_4px_0_0_rgba(180,83,9,1)] hidden sm:block">
              <div className="w-8 h-8 md:w-10 md:h-10 bg-indigo-900 rounded-lg flex items-center justify-center font-black text-yellow-400 text-lg">G</div>
            </div>
            <div className="flex flex-col">
              <h1 className="text-xl md:text-3xl font-black text-white italic tracking-tighter uppercase drop-shadow-[0_2px_4px_rgba(0,0,0,0.5)]">The Maze Pursuit</h1>
              <p className="text-indigo-300 text-xs md:text-sm font-bold mt-1 tracking-wider uppercase">Stealth Turn-Based AI</p>
            </div>
          </div>
          <div className="flex flex-wrap md:flex-nowrap gap-2 sm:gap-4 w-full md:w-auto">
            <div className="bg-indigo-800/50 rounded-full px-4 py-2 flex items-center space-x-3 border-2 border-indigo-700 flex-1 md:flex-none justify-center">
              <span className="text-xs font-black text-indigo-400 uppercase tracking-widest hidden sm:inline">Turn</span>
              <span className="font-black text-cyan-400 text-lg">{state.turn}</span>
            </div>
            <div className="bg-indigo-800/50 rounded-full px-4 py-2 flex items-center space-x-3 border-2 border-indigo-700 flex-1 md:flex-none justify-center">
              <span className="text-xs font-black text-indigo-400 uppercase tracking-widest hidden sm:inline">Active</span>
              <span className={`font-black text-sm uppercase px-2 py-1 rounded-md ${
                state.jerry.mpTracker > 0 ? 'bg-cyan-400 text-indigo-950 shadow-[0_0_10px_rgba(34,211,238,0.5)]' : 'bg-pink-500 text-white shadow-[0_0_10px_rgba(236,72,153,0.5)]'
              }`}>{state.jerry.mpTracker > 0 ? "Jerry" : "Tom"}</span>
            </div>
            <div className="bg-indigo-800/50 rounded-full px-4 py-2 flex items-center space-x-3 border-2 border-indigo-700 w-full md:w-auto justify-center relative overflow-hidden">
              {state.turn % 7 === 0 && (
                <div className="absolute inset-0 bg-pink-500/20 animate-pulse" />
              )}
              <span className="text-xs font-black text-indigo-400 uppercase tracking-widest hidden xl:inline">Tom Info</span>
              <span className={`font-black text-sm uppercase px-2 py-1 rounded-md z-10 ${
                state.tom.state === 'chase' ? 'bg-pink-500 text-white shadow-[0_0_10px_rgba(236,72,153,0.5)]' :
                state.tom.state === 'search' ? 'bg-yellow-400 text-indigo-950 shadow-[0_0_10px_rgba(250,204,21,0.5)]' : 
                'text-indigo-300'
              }`}>{state.turn % 7 === 0 ? "SCANNING!" : state.tom.state}</span>
            </div>
            <button 
              onClick={toggleDevMode}
              className={`rounded-full px-4 py-2 flex items-center space-x-2 border-2 transition-all cursor-pointer ${
                isDev ? 'bg-cyan-400 border-cyan-300 text-indigo-950 font-black scale-105 shadow-[0_0_15px_rgba(34,211,238,0.5)]' : 'bg-indigo-800/50 border-indigo-700 text-indigo-400 font-bold'
              }`}
            >
              <RefreshCcw className={`w-4 h-4 ${isDev ? 'animate-spin' : ''}`} />
              <span className="text-xs uppercase tracking-widest">Dev Mode</span>
            </button>
          </div>
        </header>

        {/* MAIN GAME AREA */}
        <div className="flex-1 flex flex-col xl:flex-row gap-6 min-h-0">
          <div className="flex-1 bg-indigo-900 border-y-4 sm:border-4 border-indigo-800 sm:rounded-3xl p-4 sm:p-6 shadow-2xl relative flex flex-col overflow-x-auto min-h-[400px]">
            {/* Visual background for the "board" container */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,#4338ca,#1e1b4b)] pointer-events-none opacity-50 z-0"></div>
            
            {/* OVERLAYS */}
            {state.status !== 'playing' && (
              <div className="absolute inset-0 z-20 bg-indigo-950/90 backdrop-blur-md flex flex-col items-center justify-center p-8 text-center animate-in fade-in zoom-in-95 duration-300">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,#4338ca_0%,transparent_70%)] opacity-30"></div>
                <h2 className={`text-5xl md:text-7xl font-black mb-4 drop-shadow-[0_4px_4px_rgba(0,0,0,0.5)] italic tracking-tighter uppercase relative z-10 ${state.status === 'jerry_won' ? 'text-green-400' : 'text-pink-500'}`}>
                  {state.status === 'jerry_won' ? 'Victory!' : 'Caught!'}
                </h2>
                <p className="text-indigo-200 mb-8 max-w-sm font-bold relative z-10 text-lg">
                  {state.status === 'jerry_won' ? 
                    'You reached the exit safely!' : 
                    'The AI outsmarted you using Minimax and spatial reasoning.'}
                </p>
                <button onClick={onRestart} className="relative z-10 bg-pink-500 hover:bg-pink-400 px-8 py-4 rounded-2xl font-black text-white shadow-[0_6px_0_0_rgba(157,23,77,1)] transition-transform active:translate-y-2 flex items-center gap-3 text-lg uppercase tracking-widest cursor-pointer">
                  <RefreshCcw className="w-6 h-6" /> Play Again
                </button>
              </div>
            )}

            <div className="flex flex-col flex-1 items-center justify-center min-w-max">
              <div className="inline-grid gap-[2px] z-10 relative" style={{ gridTemplateColumns: `repeat(${state.maze[0].length}, minmax(0, 1fr))` }}>
                {state.maze.map((row, y) => (
                row.map((cell, x) => {
                  const isWall = cell === 'wall';
                  const isExit = cell === 'exit';
                  const isVisible = visibleJerrySet.has(`${x},${y}`) || isDev;
                  const hasTom = state.tom.pos.x === x && state.tom.pos.y === y;
                  const hasJerry = state.jerry.pos.x === x && state.jerry.pos.y === y;
                  const item = state.items[y][x];
                  
                  // Traces
                  const trace = state.traces.find(t => t.pos.x === x && t.pos.y === y);
                  
                  // Audio Indicator: placed near Jerry's visible boundary if Tom is near
                  // Note: A simpler approach for the Grid is implemented in the UI layer below
                  
                  let bgClass = isDev ? 'bg-indigo-950/20' : 'bg-[#05040a]'; // Default completely hidden
                  if (isVisible) {
                    if (isWall) bgClass = isDev ? 'bg-indigo-900/50 border border-indigo-700/30' : 'bg-indigo-500 shadow-[inset_0_2px_0_rgba(255,255,255,0.4)] border-b-[3px] border-indigo-800 rounded-[4px] md:rounded-lg';
                    else if (isExit) bgClass = 'bg-green-400/20 rounded-[4px] md:rounded-lg border-2 border-green-400/50 shadow-[0_0_15px_rgba(74,222,128,0.3)] inset-shadow';
                    else bgClass = isVisible && !visibleJerrySet.has(`${x},${y}`) ? 'bg-indigo-950/40' : 'bg-indigo-950 hover:bg-indigo-800 cursor-pointer rounded-[4px] md:rounded-lg shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)]';
                  }

                  const isPathTarget = jerryTarget?.x === x && jerryTarget?.y === y;
                  const inJerryPath = state.jerryPath.some(p => p.x === x && p.y === y);
                  const inTomPath = state.tomPath.some(p => p.x === x && p.y === y);

                  return (
                    <div 
                      key={`${x}-${y}`} 
                      className={`w-6 h-6 sm:w-8 sm:h-8 xl:w-10 xl:h-10 flex items-center justify-center transition-all duration-300 relative ${bgClass}`}
                      onClick={() => handleCellClick(x, y)}
                      title={isVisible ? `(${x},${y})` : undefined}
                    >
                      {/* Fog of war hides non-static entities */}
                      {isVisible && (
                        <>
                          {isExit && !hasJerry && <DoorOpen className="w-3/5 h-3/5 text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.8)]" />}
                          {item === 'cheese' && <div className="text-sm md:text-lg relative z-10 animate-bounce">🧀</div>}
                          {item === 'bell' && <div className="text-sm md:text-lg relative z-10 animate-bounce">🔔</div>}
                          
                          {/* Traces */}
                          {!hasTom && !hasJerry && trace && (
                             <div 
                               className={`w-1.5 h-1.5 md:w-2 md:h-2 rounded-full ${trace.agent === 'tom' ? 'bg-pink-500 shadow-[0_0_10px_rgba(236,72,153,0.8)]' : 'bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]'}`} 
                               style={{ opacity: Math.max(0.2, trace.age * 0.33) }}
                             />
                          )}

                          {/* Characters */}
                          {hasTom && <div className="z-10 text-xl md:text-2xl drop-shadow-[0_4px_4px_rgba(0,0,0,0.5)] translate-y-[-2px]">🐱</div>}
                          {hasJerry && <div className="z-10 text-xl md:text-2xl drop-shadow-[0_4px_4px_rgba(0,0,0,0.5)] translate-y-[-2px]">🐭</div>}
                          
                          {/* Path indicators */}
                          {!hasJerry && inJerryPath && <div className="w-1.5 h-1.5 md:w-2 md:h-2 bg-cyan-400/80 rounded-full shadow-[0_0_8px_rgba(34,211,238,0.8)]" />}
                          {isPathTarget && <div className="absolute inset-0 border-[2px] border-cyan-400 rounded-[4px] md:rounded-lg shadow-[0_0_15px_rgba(34,211,238,0.5)] animate-pulse" />}
                          
                          {/* Tom Path (Dev Mode) */}
                          {isDev && !hasTom && inTomPath && <div className="w-1 h-1 md:w-1.5 md:h-1.5 bg-pink-500/60 rounded-full" />}
                        </>
                      )}

                        {/* Sound Indicator - Shown to player even if tile is hidden, but must be adjacent to visible */}
                        {showSoundIndicator && hasTom && !isVisible && (
                           <div className="absolute inset-0 flex items-center justify-center animate-ping">
                             <AudioWaveform className="w-4 md:w-5 h-4 md:h-5 text-pink-500" />
                           </div>
                        )}
                      </div>
                    );
                  })
                ))}
              </div>
            </div>
            
            {showSoundIndicator && (
               <div className="absolute top-4 right-4 flex items-center gap-2 px-4 py-2 bg-pink-500 text-white font-bold rounded-2xl shadow-[0_0_20px_rgba(236,72,153,0.6)] animate-pulse z-10 transition-all">
                 <AudioWaveform className="w-5 h-5 animate-bounce" />
                 Sound Nearby!
               </div>
            )}
            
          </div>

          {/* SIDEBAR LOGIC */}
          <div className="w-full md:w-72 flex flex-col gap-6 shrink-0 md:overflow-y-auto pr-2 pb-6 md:pb-0 z-10 px-4 sm:px-0">
             <div className="bg-indigo-900 border-4 border-indigo-800 rounded-3xl p-6 shadow-xl">
                <h3 className="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">Legend</h3>
                <ul className="space-y-4">
                  <li className="flex items-center gap-3 bg-indigo-950/50 rounded-xl px-3 py-2 border border-indigo-800/50">
                    <div className="text-xl drop-shadow">🐭</div> 
                    <span className="text-sm font-bold text-indigo-100 flex-1">Jerry <span className="text-indigo-400 font-normal text-xs ml-1">(You)</span></span>
                  </li>
                  <li className="flex items-center gap-3 bg-indigo-950/50 rounded-xl px-3 py-2 border border-indigo-800/50">
                    <div className="text-xl drop-shadow">🐱</div> 
                    <span className="text-sm font-bold text-pink-400 flex-1">Tom <span className="text-indigo-400 font-normal text-xs ml-1">(Minimax AI)</span></span>
                  </li>
                  <li className="flex items-center gap-3 bg-indigo-950/50 rounded-xl px-3 py-2 border border-indigo-800/50">
                    <DoorOpen className="w-5 h-5 text-green-400 drop-shadow-[0_0_10px_rgba(74,222,128,0.5)]"/> 
                    <span className="text-sm font-bold text-green-400 flex-1">Exit</span>
                  </li>
                  <li className="flex items-center gap-3 bg-indigo-950/50 rounded-xl px-3 py-2 border border-indigo-800/50">
                    <div className="text-xl">🧀</div> 
                    <span className="text-sm font-bold text-yellow-400 flex-1">Cheese <span className="text-indigo-400 font-normal text-xs ml-1">(MP+1)</span></span>
                  </li>
                  <li className="flex items-center gap-3 bg-indigo-950/50 rounded-xl px-3 py-2 border border-indigo-800/50">
                    <div className="text-xl">🔔</div> 
                    <span className="text-sm font-bold text-cyan-400 flex-1">Bell <span className="text-indigo-400 font-normal text-xs ml-1">(Sight+)</span></span>
                  </li>
                </ul>
             </div>

              <div className="bg-indigo-900 border-4 border-indigo-800 rounded-3xl p-6 shadow-xl flex-1 flex flex-col min-h-0">
                <h3 className="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">AI Intelligence</h3>
                <ul className="text-xs space-y-2 text-indigo-200 font-medium leading-relaxed mb-4">
                   <li>• <span className="text-pink-400 font-bold">Hearing:</span> Tom can hear Jerry within 7 tiles through walls.</li>
                   <li>• <span className="text-pink-400 font-bold">Global Scan:</span> Every 7 turns, Tom reveals Jerry's exact location.</li>
                   <li>• <span className="text-pink-400 font-bold">Memory:</span> Tom tracks your movement while in hearing range.</li>
                </ul>
                <p className="text-sm text-indigo-300 font-medium leading-relaxed">
                   Tom uses <span className="text-pink-400 font-bold">Minimax</span> and sound tracking to chase you. Move wisely!
                </p>
                {state.jerry.cheeseTurnsLeft > 0 && (
                  <div className="mt-auto p-4 bg-yellow-400 shadow-[0_4px_0_0_rgba(180,83,9,1)] rounded-2xl text-indigo-950 text-sm flex justify-between items-center whitespace-nowrap overflow-hidden">
                    <span className="font-black">🧀 Haste Active!</span>
                    <span className="font-black bg-indigo-950 text-yellow-400 px-2 py-1 rounded-lg text-[10px] uppercase tracking-widest">{state.jerry.cheeseTurnsLeft} left</span>
                  </div>
                )}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
