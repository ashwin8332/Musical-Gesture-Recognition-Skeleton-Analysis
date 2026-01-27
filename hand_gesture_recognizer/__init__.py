"""
Hand Gesture Recognizer
========================

A professional real-time hand gesture recognition system built with MediaPipe and OpenCV.

Basic Usage:
-----------
>>> from hand_gesture_recognizer import GestureRecognizer
>>> 
>>> recognizer = GestureRecognizer()
>>> 
>>> def on_fist(state):
...     if state == "appear":
...         print("Fist detected!")
>>> 
>>> recognizer.register_gesture("fist", on_fist)
>>> recognizer.run()

Features:
---------
- Real-time hand tracking and gesture recognition
- Support for multiple gestures (fist, open palm, peace sign, etc.)
- Swipe gesture detection
- Custom callback system
- Visual feedback with hand landmarks
- FPS monitoring
- Configurable parameters

For more information, see the documentation at:
https://github.com/yourusername/hand_gesture_recognizer
"""

from .main import GestureRecognizer

__version__ = "2.0.0"
__author__ = "Hand Gesture Recognizer Team"
__license__ = "MIT"

__all__ = ["GestureRecognizer"]

