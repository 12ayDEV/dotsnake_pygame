# Dotsnake Pygame (Web Edition)

**Dotsnake** is a hybrid Snake + Shooter arcade game where you grow by eating dots, but fight back against enemies using your tail as ammo.

## Core Mechanics

- **Snake Movement**: Classic snake controls (Arrows). You cannot stop.
- **Combat**:
  - Press **SPACE** to shoot.
  - Shooting consumes 1 segment of your tail.
  - If your tail is empty, you cannot shoot.
- **Ammo Types**:
  - **Standard (Red)**: Basic shot.
  - **Charge (Yellow)**: Piercing shot (eats 2 segments).
- **Enemies**:
  - **Chaser (Red)**: Aggressively hunts you.
  - **Follower (Orange)**: Mimics your movement history.
  - **Walls (Blue)**: Blocks path, can be broken.
- **Pause System**: Press **ESC** to pause.
  - Features a robust **Global Game Time** system to prevent visual stutter on web.
  - Includes a **Snapshot Freeze** mechanic for zero-latency pausing.

## Inner Workings & Architecture

This project is built with **Python 3.11** and **Pygame Community Edition (CE)**, designed to run in a web browser using **Pygbag**.

### Key Components:

- **`dotsnake.py`**: The game engine.
  - **`get_game_time()`**: A custom time-keeping function that replaces `pygame.time.get_ticks()`. It subtracts paused duration from real time, ensuring physics and animations freeze perfectly.
  - **`InterpolatedSprite`**: Base class for all moving entities. Uses `prev_x/y` and `last_move_time` to smoothly interpolate positions between grid ticks.
  - **`main()`**: An `async` entry point required by Pygbag's WASM runtime to yield to the browser event loop.
- **`main.py`**: A minimal wrapper that imports and runs `dotsnake.main()`.
- **`build/web/`**: The output folder containing the WASM-ready static files.

## How to Run

### 1. Locally (Development)

You can run the game purely in Python to test logic:

```bash
python dotsnake.py
```

### 2. Locally (Web Simulation)

To verify the Web Assembly build locally (highly recommended before deployment):

```bash
python run_web.py
# Serves the game at http://localhost:8000
```

*Note: Some web-specific timing behaviors might differ slightly.

*Extra-note: The code inside of index.html is designed to be a polyglot file that contains both HTML and Python scripts, please ignore the warning errors.

- Open `http://localhost:8000` in Chrome/Edge/Firefox or similar web engines.
- Wait until the game finishes rendering in the web page and displays "Ready to start!".
- Click on the web page, the game is now playable.
- Use `Ctrl+C` in terminal to stop the server.

### 3. Deploy to Web

1. Navigate to `build/web`.
2. Upload `index.html`, `dotsnake_pygame.apk`, and `favicon.png` to your web server.
3. **Critical**: Ensure your server sends Cross-Origin headers (`Cross-Origin-Opener-Policy: same-origin`).
