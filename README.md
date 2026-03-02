this is a old repo from a while ago that i havent uploaded here, this bot doesnt work with many bugs following in its creation, feel free to download and tinker with it if you'd like.

i will be attempting at remaking this and try to get it to work *hopefully*
if not then you guys can have this for now


# Taiko no Tatsujin: Rhythm Festival Bot 🥁

An automated Python bot that plays Taiko no Tatsujin: Rhythm Festival by detecting notes on screen and hitting them automatically using computer vision.

## Features

- **Real-time Note Detection** - Uses OpenCV to detect red (Don), blue (Ka), and yellow (Drumroll) notes
- **Automatic Input** - Simulates keyboard inputs to hit notes at the right time
- **Customizable Configuration** - Adjust detection areas, hit zones, colors, and timing
- **Calibration Tool** - Easy setup wizard to configure for your screen
- **Debug Overlay** - Visual feedback showing detected notes and hit zones

## Requirements

- Python 3.8 or higher
- Windows (tested), but should work on Linux/Mac with minor adjustments
- Taiko no Tatsujin: Rhythm Festival (or similar rhythm game)

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

## Quick Start

### 1. Run Calibration Tool

First, calibrate the bot for your screen:

```powershell
python calibrator.py
```

**Calibration Steps:**
- Start your game and position it on screen
- Press `1` to select the **detection area** (where notes move across)
- Click and drag to select the area
- Press `2` to select the **hit zone** (where you hit notes)
- Click and drag around the hit circle
- Press `3` to test color detection
- Press `s` to save configuration
- Press `q` to quit

Update [config.py](config.py) with the values from `calibration.json`.

### 2. Configure Settings

Edit [config.py](config.py) to match your game:

```python
# Screen capture region (adjust to your game window)
CAPTURE_REGION = {
    'x': 0,
    'y': 0,
    'width': 1920,
    'height': 1080
}

# Key bindings (match your game settings)
DON_KEYS = ['d', 'f']  # Red notes
KA_KEYS = ['j', 'k']   # Blue notes
```

### 3. Run the Bot

```powershell
python taiko_bot.py
```

**Controls:**
- `s` - Start/Stop the bot
- `q` - Quit
- `c` - Calibration reminder

## How It Works

1. **Screen Capture** - Continuously captures the game area using `mss`
2. **Color Detection** - Converts frames to HSV and detects notes by color ranges
3. **Position Tracking** - Calculates note positions and distances to hit zone
4. **Timing** - Triggers input when notes reach the optimal hit distance
5. **Input Simulation** - Sends keyboard presses using `pynput`

## Configuration Guide

### Detection Area
The rectangular region where notes appear and move. Should cover the full horizontal path of notes.

### Hit Zone
The circular area where notes should be hit. Usually the drum icon in the center.

### Color Ranges (HSV)
Adjust these if detection isn't working:
```python
# Red notes (Don)
DON_COLOR_LOWER = np.array([0, 100, 100])
DON_COLOR_UPPER = np.array([10, 255, 255])

# Blue notes (Ka)
KA_COLOR_LOWER = np.array([100, 100, 100])
KA_COLOR_UPPER = np.array([130, 255, 255])
```

### Timing
Fine-tune hit timing:
```python
INPUT_DELAY = 0.00        # Delay before hitting (adjust if hitting early/late)
HIT_THRESHOLD = 80        # Distance to trigger hit (lower = more precise)
```

## Troubleshooting

### Bot isn't detecting notes
- Run calibrator and test color detection (press `3`)
- Adjust color ranges in [config.py](config.py)
- Ensure detection area covers the full note path
- Check that game is in focus and visible

### Hitting too early/late
- Adjust `INPUT_DELAY` in [config.py](config.py)
- Increase/decrease `HIT_THRESHOLD` for earlier/later hits
- Check your system performance (aim for 60+ FPS)

### Low FPS
- Reduce `CAPTURE_REGION` size to capture less area
- Close other applications
- Disable `SAVE_DETECTIONS` if enabled

## File Structure

```
Rythm/
├── taiko_bot.py         # Main bot script
├── config.py            # Configuration settings
├── note_detector.py     # Computer vision detection
├── input_controller.py  # Keyboard input simulation
├── calibrator.py        # Calibration tool
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Advanced Features

### Note Prediction
Predicts note positions ahead of time for better accuracy:
```python
ENABLE_PREDICTION = True
PREDICTION_FRAMES = 3
```

### Debug Mode
Enable detailed logging and save detected frames:
```python
SHOW_DEBUG_INFO = True
SAVE_DETECTIONS = True
LOG_HITS = True
```

## Limitations

- Requires consistent lighting and game visuals
- May need recalibration after game updates or resolution changes
- Performance depends on your system specs
- Color detection may vary with different visual themes

## Legal Notice

This bot is for educational purposes only. Use at your own risk. Some games may have anti-cheat systems or terms of service that prohibit automation. Always check the game's terms of service before using automated tools.

## Contributing

Feel free to improve the bot:
- Better note detection algorithms
- Support for more note types (big notes, balloon notes)
- Machine learning-based detection
- GUI for easier configuration

## License

MIT License - Feel free to modify and distribute.

## Credits

Built with:
- OpenCV for computer vision
- mss for fast screen capture
- pynput for keyboard input simulation

---

**Happy drumming! 🥁**
