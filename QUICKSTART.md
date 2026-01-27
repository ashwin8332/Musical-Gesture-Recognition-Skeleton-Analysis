# 🚀 Quick Start Guide

Get started with Hand Gesture Recognition in **3 minutes**!

## Step 1: Installation (1 minute)

```bash
# Navigate to project directory
cd hand_gesture_recognizer-1.3.1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Run the App (30 seconds)

```bash
# Start in demo mode
python app.py
```

## Step 3: Try Gestures (1 minute)

1. **Show your hand** to the camera
2. **Make a fist** ✊ - See "Fist detected!" in console
3. **Open your palm** 🖐️ - See "Open palm detected!"
4. **Make a peace sign** ✌️ - Two fingers up
5. **Swipe left or right** ⬅️➡️ - Move hand quickly

Press **ESC** to exit!

---

## 🎮 Try Different Modes

### Media Control Mode
```bash
python app.py --mode media
```
Control a simulated media player with gestures!

### Counter Mode
```bash
python app.py --mode counter
```
Track your gesture statistics!

### Custom Mode
```bash
python app.py --mode custom
```
Template for your own customizations!

---

## ⌨️ Keyboard Shortcuts

- **ESC** - Exit application
- **F** - Toggle FPS counter
- **M** - Toggle mask view

---

## 🔧 Troubleshooting

### Camera not working?
```bash
# Check which cameras are available
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
```

Then edit `hand_gesture_recognizer/config.py`:
```python
DEFAULT_CAMERA_INDEX = 1  # Change to your camera number
```

### Gestures not detected?
- Ensure **good lighting**
- Position hand **30-60cm** from camera
- **Hold gestures** for at least 0.5 seconds
- Avoid cluttered backgrounds

---

## 📚 Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [API Reference](README.md#-api-reference) to build custom applications
3. Explore the source code in `hand_gesture_recognizer/` directory

---

## 🎯 Common Use Cases

### For Developers
```python
from hand_gesture_recognizer import GestureRecognizer

recognizer = GestureRecognizer()

def on_fist(state):
    if state == "appear":
        print("Do something when fist appears!")

recognizer.register_gesture("fist", on_fist)
recognizer.run()
```

### For Users
Just run:
```bash
python app.py --mode media
```
And control media with hand gestures!

---

**Need help?** Open an issue on GitHub or check the [Troubleshooting](README.md#-troubleshooting) section in README.md

**Ready to build something cool?** Check out the [Usage Examples](README.md#-usage-examples) in README.md!
