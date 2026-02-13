# Tennis Algorithm Game - Implementation Plan

## Context

Create a single-file 2D tennis game with fake 3D perspective (trapezoid court) where the player must solve programming syntax multiple-choice questions to unlock their racket and return the ball. The game runs entirely in-browser via `file:///` with no server or external dependencies. This is a study tool disguised as a game.

## File to Create

- **`tennis_game.html`** - Single self-contained HTML file with embedded CSS and JS

## Visual Design

### Court (Trapezoid / Fake 3D)
- Canvas: 800x600 pixels
- Court is a trapezoid: wide at bottom (player), narrow at top (CPU)
- Vanishing point at top-center of canvas
- Green court surface, white boundary lines converging toward vanishing point
- Net: horizontal dashed line across the middle of the trapezoid
- Service boxes and center line drawn in perspective
- No walls - ball that goes past sidelines or baseline is OUT

### Perspective Projection
- Use a `depth` value (0.0 = player/bottom, 1.0 = CPU/top)
- As depth increases toward CPU end:
  - Court width narrows (trapezoid convergence)
  - Ball shrinks (size scales with depth)
  - Ball speed appears slower (perspective foreshortening)
- Projection function maps logical (x, depth) to screen (screenX, screenY)
- Court bottom edge: ~y=550, full width ~700px centered
- Court top edge: ~y=80, narrower width ~300px centered

### Ball
- Yellow/white circle that scales with depth (large near player, small near CPU)
- Shadow underneath that also scales
- Slight oval stretching for speed effect when moving fast

### Player Racket
- Oval head on a short rectangle handle
- Scrolls left-right along the bottom edge only (no up/down movement)
- When LOCKED: red tint/glow, shows lock indicator
- When UNLOCKED: normal color, green flash on unlock
- Controls: Left/Right arrow keys (or A/D)

### CPU Racket
- Simple rectangle that scrolls left-right along the top (narrow) edge
- Slightly imperfect tracking so the CPU is beatable
- Smaller than player racket (perspective)

### Scoreboard
- Positioned in top-right corner of canvas
- Styled box with:
  - Player name ("YOU") and CPU name ("CPU")
  - Current game score (15, 30, 40, AD)
  - Games won in current set
  - Sets won (best of 3 sets, 6 games per set)
- Clean look with background panel, readable font

### Question Overlay
- Semi-transparent dark backdrop over the court
- Centered question card (white/light background, rounded corners)
- Question text at top
- 4 answer buttons (A, B, C, D) - clickable AND keyboard selectable (1-4 keys)
- Countdown timer bar (10 seconds, global variable `QUESTION_TIME_LIMIT = 10`)
- Timer visually drains as a progress bar, changes color (green -> yellow -> red)
- Category label shown (Python, JavaScript, etc.)

## Game Mechanics

### Game Flow
1. **TITLE** screen - "Tennis Algorithm Game" + "Press SPACE to start"
2. **SERVING** - Player presses SPACE, ball launches from player end toward CPU
3. **CPU_RETURN** - CPU moves to intercept, hits ball back toward player
4. **QUESTION_CHECK** - When ball crosses net heading toward player, ~50% random chance a question triggers. If no question, racket stays unlocked and player just plays normally.
5. **QUESTION_TIME** (if triggered) - Question overlay appears, ball enters **slow motion** (~20% speed). Player picks A/B/C/D within 10-second countdown timer.
   - **Correct**: Racket unlocks, overlay disappears, ball resumes normal speed, player positions racket
   - **Wrong or Timeout**: Point goes to CPU, brief "Wrong!" or "Time's Up!" flash
6. **RALLY** - Player hits ball back (or freely if no question), cycle to step 3
7. **POINT_SCORED** - Display point result, update scoreboard, return to SERVING

### Ball Physics
- Ball moves in logical coordinates: `logicalX` (0-100, left-right) and `depth` (0.0-1.0, player-to-CPU)
- Ball has `dx` (lateral movement) and `dDepth` (depth movement toward/away)
- No wall bouncing - if ball goes past logical sidelines, it's OUT
- If ball passes player's depth without being hit, point to CPU
- If ball passes CPU's depth without being hit, point to player
- Ball speed increases slightly each rally exchange for tension

### Player Controls
- Left/Right arrows or A/D: move racket left-right
- SPACE: serve
- 1/2/3/4 keys (or click): answer questions
- Racket has bounded movement within the court bottom edge

### CPU AI
- Tracks ball's logical X position with slight delay/offset
- Random error factor so it occasionally misses (increases with difficulty)
- Moves at a capped speed so it can't teleport
- Returns ball with slight random lateral angle

### Scoring (Full Tennis)
- Points: 0, 15, 30, 40, Deuce (40-40), Advantage, Game
- First to 6 games wins a set (must win by 2)
- Tiebreak at 6-6: first to 7 points, win by 2
- Best of 3 sets wins the match
- Scoreboard updates in real time
- Server alternates each game

### Question Frequency
- ~50% random chance a question appears each time ball crosses net toward player
- When no question triggers, racket stays unlocked and player plays freely
- Keeps gameplay unpredictable - sometimes pure tennis, sometimes quiz time
- Global variable `QUESTION_CHANCE = 0.5` for easy tuning

## Global Configuration Variables

```javascript
const QUESTION_TIME_LIMIT = 10;    // seconds to answer
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const BALL_BASE_SPEED = 0.015;     // depth units per frame
const QUESTION_CHANCE = 0.5;       // 50% chance question appears
const SLOW_MOTION_FACTOR = 0.2;   // ball speed during question
const CPU_SKILL = 0.7;             // 0-1, how accurate CPU is
const COURT_COLOR = "#2d7a3a";     // green court
const LINE_COLOR = "#ffffff";      // white lines
```

## Question Bank (40+ questions)

Embedded JS array of objects, each with:
```javascript
{
  category: "Python",
  question: "What is the correct way to define a function in Python?",
  choices: ["function myFunc():", "def myFunc():", "fun myFunc():", "define myFunc():"],
  answer: 1  // index of correct choice
}
```

Categories to include:
- **Python** (~15 questions): syntax, data types, list ops, string methods, loops, conditionals, functions, classes
- **JavaScript** (~10 questions): syntax, DOM, array methods, let/const/var, arrow functions, promises
- **HTML/CSS** (~10 questions): tags, selectors, box model, flexbox, semantic elements
- **SQL** (~5-8 questions): SELECT, JOIN, WHERE, GROUP BY, INSERT, CREATE TABLE
- **General** (~5 questions): data structures, Big-O, boolean logic, Git commands

Questions are shuffled at game start. No immediate repeats.

## Code Structure (inside single HTML file)

```
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Canvas centering, body background, overlay styles */
  </style>
</head>
<body>
  <canvas id="gameCanvas"></canvas>
  <script>
    // ===== CONFIGURATION =====
    // Global constants

    // ===== QUESTION BANK =====
    // Array of question objects

    // ===== GAME STATE =====
    // State machine variables, scores, ball position, racket positions

    // ===== PERSPECTIVE PROJECTION =====
    // Functions to map logical coords to screen coords

    // ===== DRAWING FUNCTIONS =====
    // drawCourt(), drawBall(), drawPlayerRacket(), drawCPURacket()
    // drawScoreboard(), drawQuestionOverlay(), drawTitleScreen()

    // ===== GAME LOGIC =====
    // updateBall(), updateCPU(), checkCollisions()
    // handleQuestion(), handleAnswer(), updateScore()

    // ===== INPUT HANDLING =====
    // Keyboard event listeners, click handlers for answers

    // ===== GAME LOOP =====
    // requestAnimationFrame main loop, state machine dispatcher

    // ===== INITIALIZATION =====
    // Setup canvas, shuffle questions, start game loop
  </script>
</body>
</html>
```

## Verification

1. Open `tennis_game.html` directly in a browser via `file:///`
2. Title screen appears, press SPACE to start
3. Ball serves toward CPU, CPU returns it
4. Question appears with countdown timer when ball crosses net toward player
5. Answering correctly unlocks racket, player can hit ball back
6. Wrong answer or timeout awards point to CPU
7. Scoreboard updates correctly through games and sets
8. Game ends with match result screen
