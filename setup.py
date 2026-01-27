"""
Setup configuration for Hand Gesture Recognizer
"""

from setuptools import setup, find_packages
import os

# Read long description from README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
with open(requirements_path, encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="hand-gesture-recognizer",
    version="2.0.0",
    description="A professional real-time hand gesture recognition system using MediaPipe and OpenCV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hand Gesture Recognizer Team",
    author_email="support@handgesturerecognizer.com",
    url="https://github.com/yourusername/hand_gesture_recognizer",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/hand_gesture_recognizer/issues",
        "Source": "https://github.com/yourusername/hand_gesture_recognizer",
        "Documentation": "https://github.com/yourusername/hand_gesture_recognizer#readme",
    },
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video :: Capture",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "gesture-recognition",
        "hand-tracking",
        "computer-vision",
        "mediapipe",
        "opencv",
        "real-time",
        "machine-learning",
        "ai",
        "gesture-control",
        "touchless-control"
    ],
    entry_points={
        "console_scripts": [
            "gesture-demo=demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
