# Typing Practice Game

A feature-rich Python typing practice game with Chinese/English bilingual interface, diverse settings, and sound feedback.

## Requirements

- Python 3.6+
- Pygame library

## Installation

1. Make sure Python 3.6 or higher is installed
2. Install Pygame:
   ```bash
   pip install pygame
   ```

## Running the Game

```bash
cd e:\EDIT\20260511_Python课综合作业\TypingGame
python typing_game.py
```

## Game Rules

1. Click "Start Game" button or press SPACE to start
2. Letters (A-Z) and numbers (0-9) will continuously fall from the top
3. Players need to press the corresponding key before the character falls
4. Correct key press eliminates the character and scores points, with a sound effect
5. A miss occurs if the character falls to the bottom
6. Statistics and rating are shown after game time ends
7. **Important: Turn off Chinese input method during gameplay, otherwise keys won't be recognized correctly**

## Features

### Core Game
- Smooth character falling animation
- Real-time virtual keyboard highlight feedback
- Detailed game statistics (score, misses, miss rate)
- Multi-level rating system (S/A/B/C/D grades)

### Bilingual Support
- Supports Simplified Chinese and English interface
- Switch language anytime in settings

### Personalization Settings
- **Window Resolution**: Multiple options from 1024x768 to 1920x1080
- **Fall Speed**: Slow/Medium/Fast/Super Fast
- **Game Duration**: Multiple options from 15 to 180 seconds
- **Keyboard Hint**: Toggle virtual keyboard display
- **Music Volume**: Slider adjustment (0-100), current value displayed next to slider

### Settings Interface Interaction
- Only one dropdown menu can be expanded at a time
- When expanding a new menu, previous unselected menus automatically restore original settings
- After adjusting volume slider, clicking "Back" restores original volume setting
- Volume slider supports drag adjustment, with real-time value display

### Sound System
- Button click sound (800Hz crisp tone at 60% volume)
- Keyboard key elimination sound (same as button tone)
- Background music playback (optional, requires bgm.mp3 file)
- All sound volumes adjustable

### Visual Effects
- Semi-transparent background boxes and borders
- Custom background image support
- Default solid color backgrounds (menu-red, game-blue, ending-green)
- Virtual keyboard with underlines on F, J, and 0 keys

### ESC Early Exit Mechanism
- Press ESC twice to exit early during gameplay
- First ESC press shows prompt, press again within 5 seconds for early termination
- Early termination doesn't show rating, only statistics
- Virtual keyboard ESC key highlights in green when waiting for second press

## Controls

### Main Menu
- **Start Game**: Click button or press SPACE
- **Settings**: Click to enter settings menu
- **Exit Game**: Click and confirm to exit

### Game Interface
- **Letter/Number Keys**: Eliminate corresponding character
- **ESC Key**: First press shows prompt, second press ends game early

### Settings Interface
- Dropdown menu: Click to expand options
- Volume slider: Drag to adjust, value shown to the right
- Apply/Back: Click to confirm or cancel settings

## File Structure

```
TypingGame/
├── typing_game.py      # Main game program
├── README.md          # Documentation (Chinese)
├── readme_en.md       # Documentation (English)
├── config.json        # Config file (auto-generated)
├── images/            # Background images directory (optional)
│   ├── menu_bg.png    # Main menu background
│   ├── game_bg.png    # Game background
│   └── gameover_bg.png # Game over background
└── music/             # Music directory (optional)
    └── bgm.mp3        # Background music
```

## Customization

### Background Images
Create an `images` folder in the project root and place these images:
- `menu_bg.png` - Main menu background
- `game_bg.png` - Game background
- `gameover_bg.png` - Game over background

### Background Music
Create a `music` folder in the project root and place a `bgm.mp3` file for automatic playback.

### Config File
`config.json` automatically saves your settings including:
- Resolution, game speed, duration
- Language selection
- Keyboard hint toggle
- Music volume

## Rating Criteria

| Grade | Miss Rate | Description |
|-------|-----------|-------------|
| S     | < 3%      | Perfect     |
| A     | 3% - 10%  | Excellent   |
| B     | 10% - 20% | Good        |
| C     | 20% - 40% | Pass        |
| D     | > 40%     | Needs Work  |

**Note**: No rating is shown when exiting early with ESC

## FAQ

**Q: "No module named 'pygame'" error when running?**
A: Run `pip install pygame`

**Q: Background images not showing?**
A: Ensure images are in the `images` folder, format must be PNG

**Q: No music playing?**
A: Ensure `music/bgm.mp3` file exists

**Q: Can't type Chinese characters in game?**
A: Make sure Chinese input method is turned off before starting the game
