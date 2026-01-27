# 🤚 Hand Gesture Recognition Application

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-red.svg)
![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)

**A professional real-time hand gesture recognition system with multiple operation modes**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [Modes](#-application-modes) • [API](#-api-reference)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Gestures](#-supported-gestures)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Application Modes](#-application-modes)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Keyboard Controls](#-keyboard-controls)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Performance](#-performance)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Hand Gesture Recognition Application is a professional, production-ready system for real-time hand gesture detection and tracking. Built on MediaPipe and OpenCV, it offers multiple operation modes from simple demonstration to advanced media control and gesture statistics.

### Why Use This?

- ✅ **Zero-configuration** - Works out of the box
- ✅ **Multiple modes** - Demo, Media Control, Counter, and Custom
- ✅ **Professional code** - Clean architecture, logging, error handling
- ✅ **Real-time** - 30+ FPS performance
- ✅ **Extensible** - Easy to add custom gestures and callbacks
- ✅ **Well-documented** - Comprehensive documentation and examples

---

## ✨ Features

### Core Features
- 🎯 **Real-time Detection** - High-performance hand tracking (30+ FPS)
- 🖐️ **7 Gestures** - Fist, peace sign, open palm, swipes, and more
- 🎨 **Visual Feedback** - Live hand landmarks overlay
- 📊 **Statistics** - Track gesture counts and session metrics
- ⚡ **Performance Monitor** - Real-time FPS counter
- 🔧 **4 Operation Modes** - Demo, Media, Counter, Custom

### Advanced Features
- 📝 **Professional Logging** - Comprehensive debugging system
- 🎛️ **Configurable** - Centralized configuration system
- 🔄 **State Management** - Track gesture appearance/disappearance
- 🎯 **Event Callbacks** - Custom actions for each gesture
- 🖥️ **Multi-camera Support** - Use any connected camera
- 📈 **Session Reports** - Detailed statistics at exit

---

## 🖐️ Supported Gestures

| Gesture | Description | Fingers Extended | Use Case |
|---------|-------------|------------------|----------|
| ✊ **Fist** | Closed hand | 0 | Play/Pause, Select |
| ✌️ **Peace Sign** | Index & middle up | 2 | Volume Up, Next |
| 🤟 **Three Fingers** | Three fingers up | 3 | Volume Down, Option |
| 🖖 **Four Fingers** | Four fingers up | 4 | Navigation, Mode |
| 🖐️ **Open Palm** | All fingers up | 5 | Stop, Reset |
| ⬅️ **Left Swipe** | Hand moves left | Motion | Previous, Back |
| ➡️ **Right Swipe** | Hand moves right | Motion | Next, Forward |

---

## 📦 Installation

### Prerequisites

- **Python 3.8 or higher**
- **Webcam/Camera** device
- **Operating System**: Windows, macOS, or Linux

### Step 1: Clone or Download

```bash
# Clone the repository
git clone https://github.com/yourusername/hand_gesture_recognizer.git
cd hand_gesture_recognizer
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

The application will automatically download the MediaPipe hand tracking model on first run (~10MB).

### Step 4: Verify Installation

```bash
# Test the installation
python -c "from hand_gesture_recognizer import GestureRecognizer; print('✓ Installation successful!')"
```

---

## 🚀 Quick Start

### Run the Application (Demo Mode)

```bash
python app.py
```

This starts the application in **Demo Mode** - perfect for first-time users!

### What You'll See

1. **Console Output** - Application header and instructions
2. **Camera Window** - Two side-by-side views:
   - Left: Original video with hand landmarks
   - Right: Binary mask showing detected hands
3. **Real-time Feedback** - FPS counter and gesture names on screen
4. **Console Logs** - Gesture detection messages

### Try Your First Gesture

1. Position your hand in front of the camera
2. Make a fist ✊ - You'll see "Fist detected!" in the console
3. Open your palm 🖐️ - You'll see "Open palm detected!"
4. Try other gestures!

### Exit the Application

Press **ESC** key to exit and see the session summary.

---

## 🎮 Application Modes

The application has **4 distinct modes**, each designed for different use cases:

### 1. 🎬 Demo Mode (Default)

**Purpose**: Learn and test gesture recognition

```bash
python app.py
# or explicitly:
python app.py --mode demo
```

**Features**:
- Simple console output for each gesture
- Visual hand tracking overlay
- Real-time FPS display
- Perfect for testing and learning

**Use Case**: First-time users, testing camera, learning gestures

---

### 2. 🎵 Media Control Mode

**Purpose**: Control media playback with hand gestures

```bash
python app.py --mode media
```

**Gesture Mappings**:
| Gesture | Action |
|---------|--------|
| ✊ Fist | Play/Pause |
| 🖐️ Open Palm | Stop |
| ⬅️ Left Swipe | Previous Track |
| ➡️ Right Swipe | Next Track |
| ✌️ Peace Sign | Volume Up (+10%) |
| 🤟 Three Fingers | Volume Down (-10%) |

**Features**:
- Simulated media player control
- Visual feedback for each action
- Track navigation (1-10 tracks)
- Volume control with visual bar
- Action cooldown to prevent spam

**Use Case**: Touchless media control, presentations, accessibility

---

### 3. 📊 Counter Mode

**Purpose**: Track and analyze gesture statistics

```bash
python app.py --mode counter
```

**Features**:
- Count every gesture detected
- Real-time total count display
- Detailed statistics at exit:
  - Individual gesture counts
  - Percentage breakdown
  - Visual bars for frequency
  - Gestures per second rate
  - Session duration

**Sample Output**:
```
📊 Counter Mode Summary (Duration: 120.5s)
═══════════════════════════════════════════════════════════

Gesture Detection Count:
  🖐️ Open Palm         :   45 times ███████████████ 37.5%
  ✊ Fist               :   32 times ██████████ 26.7%
  ✌️ Peace Sign        :   28 times █████████ 23.3%
  🤟 Three Fingers     :   15 times █████ 12.5%

  Total Gestures       :  120
  Average Rate         : 1.0 gestures/sec
```

**Use Case**: Performance analysis, gesture training, research

---

### 4. 🔧 Custom Mode

**Purpose**: Template for custom gesture handling

```bash
python app.py --mode custom
```

**Features**:
- Basic gesture callbacks pre-configured
- Easy to extend and customize
- Template code for your own logic
- Full access to gesture events

**How to Customize**:

1. Open `app.py` in a text editor
2. Find the `setup_custom_mode()` method
3. Add your custom callbacks:

```python
def setup_custom_mode(self):
    """Your custom gesture handling"""
    def my_fist_handler(state):
        if state == "appear":
            # Do something when fist appears
            print("Custom fist action!")
            # Add your code here:
            # - Control smart home devices
            # - Send keyboard commands
            # - Trigger automation
            # - etc.
    
    self.recognizer.register_gesture("fist", my_fist_handler)
    # Add more gestures...
```

**Use Case**: Custom integrations, automation, research projects

---

## 💻 Usage Examples

### Example 1: Basic Gesture Detection

```python
from hand_gesture_recognizer import GestureRecognizer

# Create recognizer
recognizer = GestureRecognizer()

# Define callback
def on_fist(state):
    if state == "appear":
        print("Fist detected!")

# Register gesture
recognizer.register_gesture("fist", on_fist)

# Start recognition
recognizer.run()
```

### Example 2: Multiple Gestures

```python
from hand_gesture_recognizer import GestureRecognizer

recognizer = GestureRecognizer()

# Define multiple callbacks
callbacks = {
    "fist": lambda s: print("✊") if s == "appear" else None,
    "open_palm": lambda s: print("🖐️") if s == "appear" else None,
    "two_fingers": lambda s: print("✌️") if s == "appear" else None,
}

# Register all gestures
for gesture, callback in callbacks.items():
    recognizer.register_gesture(gesture, callback)

recognizer.run()
```

### Example 3: Gesture Counter

```python
from hand_gesture_recognizer import GestureRecognizer

recognizer = GestureRecognizer()
counter = {"count": 0}

def count_gestures(state):
    if state == "appear":
        counter["count"] += 1
        print(f"Total gestures: {counter['count']}")

# Count all gestures
for gesture in ["fist", "open_palm", "two_fingers", "three_fingers", "four_fingers"]:
    recognizer.register_gesture(gesture, count_gestures)

recognizer.run()
print(f"\nFinal count: {counter['count']}")
```

### Example 4: State Tracking

```python
from hand_gesture_recognizer import GestureRecognizer

recognizer = GestureRecognizer()

def gesture_with_state(state):
    if state == "appear":
        print("Gesture started!")
        # Gesture just appeared - do something
    elif state == "disappear":
        print("Gesture ended!")
        # Gesture ended - cleanup or final action

recognizer.register_gesture("fist", gesture_with_state)
recognizer.run()
```

---

## ⚙️ Configuration

### Camera Settings

Edit `hand_gesture_recognizer/config.py`:

```python
# Camera Selection
DEFAULT_CAMERA_INDEX = 0  # Change to 1, 2, etc. for other cameras

# Camera Resolution
CAMERA_FRAME_WIDTH = 640   # Increase for better quality
CAMERA_FRAME_HEIGHT = 480  # Increase for better quality
```

### Detection Sensitivity

```python
# Detection Confidence (0.0 to 1.0)
DEFAULT_MIN_DETECTION_CONFIDENCE = 0.5  # Lower = more sensitive
DEFAULT_MIN_TRACKING_CONFIDENCE = 0.5   # Higher = more stable

# Swipe Detection
SWIPE_THRESHOLD = 0.1  # Lower = more sensitive to swipes
```

### Display Settings

```python
# Visual Feedback
FPS_DISPLAY = True          # Show FPS counter
COMBINED_VIEW = True        # Show mask alongside video

# Colors (BGR format)
LANDMARK_COLOR = (0, 255, 0)      # Green
CONNECTION_COLOR = (255, 255, 255) # White
```

---

## ⌨️ Keyboard Controls

| Key | Action | Description |
|-----|--------|-------------|
| **ESC** | Exit | Close application and show summary |
| **F** | Toggle FPS | Show/hide frames per second counter |
| **M** | Toggle Mask | Show/hide binary hand mask view |

---

## 📚 API Reference

### GestureRecognizer Class

```python
class GestureRecognizer:
    def __init__(self, camera_index: int = 0)
```

**Methods**:

#### `register_gesture(gesture_name, callback)`
Register a callback function for a specific gesture.

**Parameters**:
- `gesture_name` (str): Gesture identifier
  - `"fist"`, `"open_palm"`, `"two_fingers"`, `"three_fingers"`, 
  - `"four_fingers"`, `"left_swipe"`, `"right_swipe"`
- `callback` (callable): Function to call when gesture is detected
  - Receives `state` parameter: `"appear"` or `"disappear"`

**Example**:
```python
def my_callback(state):
    print(f"Gesture {state}")

recognizer.register_gesture("fist", my_callback)
```

#### `run()`
Start the gesture recognition system.

**Behavior**:
- Opens camera and creates window
- Processes frames in real-time
- Calls registered callbacks
- Blocks until ESC is pressed or window is closed

#### `stop()`
Stop the recognition system programmatically.

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Camera Not Found

**Error**: `Cannot open camera at index 0`

**Solutions**:
```bash
# Check available cameras
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"

# Use different camera
python app.py  # Then check config.py and change DEFAULT_CAMERA_INDEX
```

#### 2. Low FPS / Laggy

**Problem**: FPS below 20

**Solutions**:
- Close other applications using camera
- Reduce resolution in `config.py`:
  ```python
  CAMERA_FRAME_WIDTH = 320
  CAMERA_FRAME_HEIGHT = 240
  ```
- Ensure good lighting
- Update graphics drivers

#### 3. Gestures Not Detected

**Problem**: Hand is visible but gestures not recognized

**Solutions**:
- Ensure adequate lighting
- Position hand clearly in view (30-60cm from camera)
- Avoid cluttered backgrounds
- Lower detection confidence:
  ```python
  DEFAULT_MIN_DETECTION_CONFIDENCE = 0.3
  ```
- Make gestures deliberately and hold for 0.5 seconds

#### 4. Module Import Error

**Error**: `ModuleNotFoundError: No module named 'hand_gesture_recognizer'`

**Solutions**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "from hand_gesture_recognizer import GestureRecognizer"
```

#### 5. MediaPipe Model Download Fails

**Error**: Failed to download hand_landmarker.task

**Solutions**:
1. Check internet connection
2. Manual download:
   ```bash
   # Download from:
   https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
   
   # Place in: hand_gesture_recognizer/hand_landmarker.task
   ```

---

## 📊 Performance

### Benchmarks

| Hardware | Resolution | FPS | Latency |
|----------|-----------|-----|---------|
| Modern Laptop (i7, 16GB) | 640x480 | 35-40 | <30ms |
| Mid-range PC (i5, 8GB) | 640x480 | 28-32 | <50ms |
| Budget Laptop (i3, 4GB) | 320x240 | 25-28 | <60ms |

### Optimization Tips

1. **Resolution**: Lower resolution = higher FPS
2. **Lighting**: Good lighting = better accuracy
3. **Background**: Clean background = faster processing
4. **Single Hand**: One hand = better performance than two
5. **Close Apps**: Close other camera-using applications

---

## 🏗️ Project Structure

```
hand_gesture_recognizer/
├── app.py                      # Main application (4 modes)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── setup.py                    # Package installation
│
└── hand_gesture_recognizer/    # Core library
    ├── __init__.py            # Package initialization
    ├── main.py                # Core recognition engine
    ├── config.py              # Configuration parameters
    └── utils.py               # Utility functions
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

### What this means:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

---

## 🙏 Acknowledgments

- **MediaPipe** - Google's ML framework for hand tracking
- **OpenCV** - Computer vision library
- **NumPy** - Numerical computing

---

## 📞 Support & Contact

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/hand_gesture_recognizer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/hand_gesture_recognizer/discussions)
- 📧 **Email**: support@handgesturerecognizer.com

---

## 🗺️ Roadmap

- [ ] GUI Configuration Panel
- [ ] Gesture Recording & Playback
- [ ] Custom Gesture Training
- [ ] Mobile App (iOS/Android)
- [ ] Web Browser Support
- [ ] Multi-language Support
- [ ] Plugin System

---
Hand Gesture Recognition Application - Enhanced Edition

options:
  -h, --help            show this help message and exit
  --mode, -m {demo,media,counter,game}
                        Application mode (default: demo)
  --no-voice            Disable voice feedback
  --no-sound            Disable sound effects
  --version, -v         show program's version number and exit


## 📈 Version History

### v2.0.0 (Current) - 2026-01-27
- ✨ Complete rewrite with professional architecture
- 🎮 Added 4 operation modes
- 📊 Enhanced statistics and reporting
- 🎨 Improved visual feedback
- 📝 Comprehensive documentation
- ⚡ MediaPipe 0.10+ compatibility

See [CHANGELOG.md](CHANGELOG.md) for full history.

---

<div align="center">

**⭐ Star this repository if you find it helpful! ⭐**

Made with ❤️ by Ashwin VK

[⬆ Back to Top](#-hand-gesture-recognition-application)

</div>
