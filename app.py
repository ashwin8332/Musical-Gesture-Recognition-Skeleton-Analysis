#!/usr/bin/env python3
"""
Hand Gesture Recognizer Application - Music + Skeleton Edition
Version 3.0.0

Musical hand gesture recognizer with skeleton visualization and accurate detection.
"""

import argparse
import logging
import sys
import time
from collections import deque, Counter
from typing import Dict, Optional
import numpy as np
import pygame
import cv2

from hand_gesture_recognizer.main import GestureRecognizer, mp_hands, mp_drawing
from hand_gesture_recognizer.config import (
    DEFAULT_MIN_DETECTION_CONFIDENCE,
    DEFAULT_MIN_TRACKING_CONFIDENCE,
    WINDOW_NAME
)
from hand_gesture_recognizer.utils import (
    SkeletonAnalyzer, draw_skeleton_analysis, draw_3d_skeleton,
    create_analysis_panel, draw_landmark_coordinates
)



class MusicSynthesizer:
    """Generates musical notes using pygame mixer."""
    
    # Musical scale mapping (C Major Scale with octaves)
    GESTURE_TO_NOTE = {
        "fist": ("C4", 261.63),           # Do
        "open_palm": ("E4", 329.63),      # Mi
        "two_fingers": ("G4", 392.00),    # Sol
        "three_fingers": ("A4", 440.00),  # La
        "four_fingers": ("C5", 523.25),   # Do (higher)
        "Pointing_Up": ("D4", 293.66),    # Re
        "Victory": ("F4", 349.23),        # Fa
        "Thumb_Up": ("B4", 493.88),       # Ti
        "ILoveYou": ("G5", 783.99),       # Sol (higher)
    }
    
    def __init__(self, sample_rate=22050):
        """Initialize the music synthesizer."""
        pygame.mixer.init(frequency=sample_rate, channels=1)
        self.sample_rate = sample_rate
        self.active_sounds = {}
        self.last_note = None
        self.note_duration = 0.3  # seconds
        
    def generate_tone(self, frequency: float, duration: float = 0.3) -> pygame.mixer.Sound:
        """Generate a musical tone."""
        n_samples = int(round(duration * self.sample_rate))
        
        # Create array for audio samples
        buf = np.zeros((n_samples, 2), dtype=np.int16)
        max_sample = 2 ** (16 - 1) - 1
        
        # Generate sine wave with envelope for smooth sound
        for i in range(n_samples):
            # ADSR envelope (simplified)
            if i < n_samples * 0.1:  # Attack
                envelope = i / (n_samples * 0.1)
            elif i > n_samples * 0.7:  # Release
                envelope = 1 - (i - n_samples * 0.7) / (n_samples * 0.3)
            else:  # Sustain
                envelope = 1.0
            
            # Generate tone with harmonics for richer sound
            sample = np.sin(2 * np.pi * frequency * i / self.sample_rate)
            sample += 0.3 * np.sin(4 * np.pi * frequency * i / self.sample_rate)  # 2nd harmonic
            sample += 0.15 * np.sin(6 * np.pi * frequency * i / self.sample_rate)  # 3rd harmonic
            
            sample = int(sample * envelope * max_sample * 0.5)
            buf[i] = [sample, sample]  # Stereo
        
        return pygame.mixer.Sound(buffer=buf)
    
    def play_note(self, gesture: str) -> Optional[str]:
        """
        Play a musical note for the given gesture.
        
        Returns:
            Note name if played, None otherwise
        """
        if gesture in self.GESTURE_TO_NOTE:
            note_name, frequency = self.GESTURE_TO_NOTE[gesture]
            
            # Don't replay the same note immediately
            if self.last_note != note_name:
                sound = self.generate_tone(frequency, self.note_duration)
                sound.play()
                self.last_note = note_name
                return note_name
        
        return None
    
    def cleanup(self):
        """Clean up pygame mixer."""
        pygame.mixer.quit()


class GestureStabilizer:
    """Stabilizes gesture detection to improve accuracy."""
    
    def __init__(self, window_size=5, threshold=0.6):
        """
        Initialize the stabilizer.
        
        Args:
            window_size: Number of frames to consider for smoothing
            threshold: Minimum ratio of frames that must agree (0.0-1.0)
        """
        self.window_size = window_size
        self.threshold = threshold
        self.gesture_history = deque(maxlen=window_size)
        
    def add_gesture(self, gesture: Optional[str]) -> Optional[str]:
        """
        Add a gesture and return the stabilized result.
        
        Args:
            gesture: Current detected gesture
            
        Returns:
            Stabilized gesture or None
        """
        self.gesture_history.append(gesture)
        
        if len(self.gesture_history) < self.window_size:
            return None
        
        # Count occurrences
        counts = Counter(self.gesture_history)
        
        # Remove None count
        if None in counts:
            del counts[None]
        
        if not counts:
            return None
        
        # Get most common gesture
        most_common = counts.most_common(1)[0]
        gesture, count = most_common
        
        # Check if it meets threshold
        if count / self.window_size >= self.threshold:
            return gesture
        
        return None


class GestureStatistics:
    """Tracks gesture statistics for summary."""
    
    def __init__(self):
        self.gesture_counts = Counter()
        self.total_detections = 0
        self.session_start = time.time()
        self.gesture_sequence = []
        
    def record_gesture(self, gesture: str):
        """Record a detected gesture."""
        self.gesture_counts[gesture] += 1
        self.total_detections += 1
        self.gesture_sequence.append((time.time(), gesture))
        
    def get_summary(self) -> str:
        """Generate a summary report."""
        duration = time.time() - self.session_start
        
        lines = [
            "\n" + "="*70,
            "🎵 MUSICAL GESTURE RECOGNITION SESSION SUMMARY 🎵",
            "="*70,
            f"Session Duration: {duration:.1f} seconds",
            f"Total Gestures Detected: {self.total_detections}",
            "",
            "Gesture Frequency:"
        ]
        
        # Sort by count
        for gesture, count in self.gesture_counts.most_common():
            percentage = (count / self.total_detections * 100) if self.total_detections > 0 else 0
            bar = "█" * int(percentage / 2)
            lines.append(f"  {gesture:20s} {count:4d} ({percentage:5.1f}%) {bar}")
        
        lines.append("")
        lines.append("Recent Gesture Sequence (last 10):")
        for timestamp, gesture in self.gesture_sequence[-10:]:
            elapsed = timestamp - self.session_start
            lines.append(f"  [{elapsed:6.1f}s] {gesture}")
        
        lines.append("="*70)
        
        return "\n".join(lines)


class MusicalGestureApp:
    """Main application with musical gesture recognition and skeleton visualization."""
    
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.recognizer = GestureRecognizer(camera_index=camera_id)
        self.synthesizer = MusicSynthesizer()
        self.stabilizer = GestureStabilizer(window_size=5, threshold=0.6)
        self.statistics = GestureStatistics()
        self.analyzer = SkeletonAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Display options
        self.show_3d = True
        self.show_panel = True
        self.show_skeleton_details = True
        
        # State tracking
        self.last_displayed_gesture = None
        self.last_note_time = 0
        self.note_cooldown = 0.2  # seconds between notes
        
        # Register gesture callbacks
        self._register_callbacks()
        
    def _register_callbacks(self):
        """Register callbacks for gesture detection."""
        gestures = ["fist", "open_palm", "two_fingers", "three_fingers", 
                   "four_fingers", "Pointing_Up", "Victory", "Thumb_Up", "ILoveYou"]
        
        for gesture in gestures:
            self.recognizer.register_gesture(gesture, self._on_gesture_detected)
    
    def _on_gesture_detected(self, state: str):
        """Callback when gesture state changes."""
        pass  # Handled in main loop
    
    def _display_gesture_terminal(self, gesture: str, note: Optional[str] = None):
        """Display gesture detection in terminal with formatting."""
        current_time = time.time()
        
        # Only display if gesture changed
        if gesture != self.last_displayed_gesture:
            timestamp = time.strftime("%H:%M:%S")
            
            # Gesture to emoji mapping
            emoji_map = {
                "fist": "✊",
                "open_palm": "🖐️",
                "two_fingers": "✌️",
                "three_fingers": "🤟",
                "four_fingers": "🖖",
                "Pointing_Up": "☝️",
                "Victory": "✌️",
                "Thumb_Up": "👍",
                "ILoveYou": "🤟"
            }
            
            emoji = emoji_map.get(gesture, "👋")
            note_str = f" → Note: {note}" if note else ""
            
            print(f"[{timestamp}] {emoji}  Detected: {gesture:20s}{note_str}")
            
            self.last_displayed_gesture = gesture
    
    def run(self):
        """Run the musical gesture recognition application with skeleton visualization."""
        print("\n" + "="*80)
        print("🎵 MUSICAL HAND GESTURE RECOGNITION + SKELETON ANALYSIS 🦴")
        print("="*80)
        print(f"Camera: {self.camera_id}")
        print("\n🎹 Gesture-to-Note Mapping:")
        
        for gesture, (note, freq) in MusicSynthesizer.GESTURE_TO_NOTE.items():
            print(f"  {gesture:20s} → {note} ({freq:.2f} Hz)")
        
        print("\n📋 Controls:")
        print("  ESC - Exit and show summary")
        print("  F   - Toggle FPS display")
        print("  3   - Toggle 3D skeleton view")
        print("  P   - Toggle analysis panel")
        print("  S   - Toggle skeleton details")
        print("="*80)
        print("\n🎼 Listening for gestures...\n")
        
        try:
            self.recognizer.running = True
            
            cap = cv2.VideoCapture(self.camera_id)
            
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open camera {self.camera_id}")
            
            # Set resolution for balanced display
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            prev_time = 0
            
            with mp_hands.Hands(
                min_detection_confidence=DEFAULT_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=DEFAULT_MIN_TRACKING_CONFIDENCE,
                max_num_hands=2  # Allow both hands
            ) as hands:
                
                while self.recognizer.running and cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        continue
                    
                    # Process image
                    image = cv2.flip(image, 1)
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    rgb_image.flags.writeable = False
                    results = hands.process(rgb_image)
                    
                    rgb_image.flags.writeable = True
                    image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
                    
                    h, w, _ = image.shape
                    detected_gestures = []  # Track gestures from both hands
                    
                    # Resize main image to standard size for balanced layout
                    target_width = 640
                    target_height = 480
                    image_resized = cv2.resize(image, (target_width, target_height))
                    
                    if results and results.multi_hand_landmarks:
                        # Different colors for left and right hand
                        hand_colors = [
                            (mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                             mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)),
                            (mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=3),
                             mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2))
                        ]
                        
                        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                            # Update analyzer
                            self.analyzer.update_history(hand_landmarks.landmark)
                            
                            # Detect gesture
                            raw_gesture = self.recognizer.detect_gesture(hand_landmarks)
                            current_gesture = self.stabilizer.add_gesture(raw_gesture)
                            
                            if current_gesture:
                                detected_gestures.append(current_gesture)
                                # Record statistics
                                self.statistics.record_gesture(current_gesture)
                                
                                # Play note with cooldown
                                current_time = time.time()
                                if current_time - self.last_note_time > self.note_cooldown:
                                    note = self.synthesizer.play_note(current_gesture)
                                    if note:
                                        self.last_note_time = current_time
                                        hand_label = "Left" if idx == 0 else "Right"
                                        self._display_gesture_terminal(f"{hand_label} Hand: {current_gesture}", note)
                            
                            # Draw skeleton analysis on resized image
                            color_spec = hand_colors[min(idx, 1)]
                            if self.show_skeleton_details:
                                image_resized = draw_skeleton_analysis(
                                    image_resized, hand_landmarks, self.analyzer,
                                    show_labels=True,
                                    show_angles=True,
                                    show_distances=True
                                )
                            else:
                                # Just draw basic landmarks with different colors per hand
                                mp_drawing.draw_landmarks(
                                    image_resized,
                                    hand_landmarks,
                                    mp_hands.HAND_CONNECTIONS,
                                    color_spec[0],
                                    color_spec[1]
                                )
                    
                    # Add title and info overlay on main image
                    cv2.rectangle(image_resized, (0, 0), (target_width, 150), (0, 0, 0), -1)
                    cv2.rectangle(image_resized, (0, 0), (target_width, 150), (0, 255, 0), 2)
                    cv2.putText(image_resized, "DUAL HAND TRACKING", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Display detected gestures
                    if detected_gestures:
                        gesture_text = " + ".join(detected_gestures)
                        # Get combined note info
                        notes = []
                        for gesture in detected_gestures:
                            if gesture in MusicSynthesizer.GESTURE_TO_NOTE:
                                note_name, freq = MusicSynthesizer.GESTURE_TO_NOTE[gesture]
                                notes.append(f"{note_name}")
                        
                        note_info = f" - Notes: {' + '.join(notes)}" if notes else ""
                        cv2.putText(image_resized, f"Gestures: {gesture_text}{note_info}", (10, 70),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Show hand count
                        hand_count = len(results.multi_hand_landmarks) if results and results.multi_hand_landmarks else 0
                        cv2.putText(image_resized, f"Hands Detected: {hand_count}", (10, 100),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 128, 0), 2)
                    else:
                        cv2.putText(image_resized, "No gesture detected", (10, 70),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
                    
                    # Calculate FPS
                    current_time = time.time()
                    fps = 1 / (current_time - prev_time) if prev_time > 0 else 0
                    prev_time = current_time
                    
                    if self.recognizer.show_fps:
                        cv2.putText(image_resized, f"FPS: {fps:.1f}", (10, 130),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    # Create right panel with 3D skeleton and analysis
                    right_panel_width = target_width
                    right_panel_height = target_height
                    
                    if results and results.multi_hand_landmarks:
                        # Create 3D skeleton visualization for both hands
                        skeleton_3d = np.zeros((right_panel_height, right_panel_width, 3), dtype=np.uint8)
                        skeleton_3d[:] = (20, 20, 20)  # Dark background
                        
                        # Draw both hands in 3D space
                        num_hands = len(results.multi_hand_landmarks)
                        
                        if num_hands == 1:
                            # Single hand - center it
                            hand_3d = draw_3d_skeleton(
                                results.multi_hand_landmarks[0].landmark, 
                                size=min(right_panel_width, right_panel_height)
                            )
                            hand_3d_resized = cv2.resize(hand_3d, (right_panel_width, right_panel_height))
                            skeleton_3d = hand_3d_resized
                            
                        elif num_hands == 2:
                            # Two hands - split view
                            split_width = right_panel_width // 2
                            
                            # Left hand
                            hand1_3d = draw_3d_skeleton(
                                results.multi_hand_landmarks[0].landmark, 
                                size=split_width
                            )
                            hand1_3d_resized = cv2.resize(hand1_3d, (split_width, right_panel_height))
                            
                            # Right hand
                            hand2_3d = draw_3d_skeleton(
                                results.multi_hand_landmarks[1].landmark, 
                                size=split_width
                            )
                            hand2_3d_resized = cv2.resize(hand2_3d, (split_width, right_panel_height))
                            
                            # Combine side by side
                            skeleton_3d = np.hstack([hand1_3d_resized, hand2_3d_resized])
                            
                            # Add separator line
                            cv2.line(skeleton_3d, (split_width, 0), (split_width, right_panel_height), 
                                   (255, 255, 255), 2)
                            
                            # Add labels
                            cv2.putText(skeleton_3d, "Hand 1", (10, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(skeleton_3d, "Hand 2", (split_width + 10, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # Add title overlay on 3D view
                        cv2.rectangle(skeleton_3d, (0, 0), (right_panel_width, 50), (0, 0, 0), -1)
                        cv2.rectangle(skeleton_3d, (0, 0), (right_panel_width, 50), (255, 0, 255), 2)
                        
                        title_text = f"3D SKELETON - {num_hands} HAND{'S' if num_hands > 1 else ''}"
                        cv2.putText(skeleton_3d, title_text, (10, 35),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                        
                        # Add analysis data overlay on 3D view
                        analysis = self.analyzer.get_analysis_summary(results.multi_hand_landmarks[0].landmark)
                        
                        # Hand openness indicator
                        if 'hand_openness' in analysis:
                            openness = analysis['hand_openness']
                            y_pos = right_panel_height - 120
                            cv2.rectangle(skeleton_3d, (10, y_pos), (right_panel_width - 10, y_pos + 110), 
                                        (0, 0, 0), -1)
                            cv2.rectangle(skeleton_3d, (10, y_pos), (right_panel_width - 10, y_pos + 110),
                                        (255, 255, 0), 2)
                            
                            cv2.putText(skeleton_3d, "Hand Analysis", (20, y_pos + 25),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            if num_hands == 1:
                                cv2.putText(skeleton_3d, f"Openness: {openness*100:.0f}%", (20, y_pos + 55),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            else:
                                # Show combined info for both hands
                                cv2.putText(skeleton_3d, f"Hand 1 Open: {openness*100:.0f}%", (20, y_pos + 50),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                                if len(results.multi_hand_landmarks) > 1:
                                    analysis2 = self.analyzer.get_analysis_summary(results.multi_hand_landmarks[1].landmark)
                                    openness2 = analysis2.get('hand_openness', 0)
                                    cv2.putText(skeleton_3d, f"Hand 2 Open: {openness2*100:.0f}%", (20, y_pos + 70),
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)
                            
                            # Progress bar for first hand
                            bar_width = int((right_panel_width - 40) * openness)
                            cv2.rectangle(skeleton_3d, (20, y_pos + 85), (20 + bar_width, y_pos + 95),
                                        (0, 255, 0), -1)
                            cv2.rectangle(skeleton_3d, (20, y_pos + 85), (right_panel_width - 20, y_pos + 95),
                                        (255, 255, 255), 1)
                            
                            # Average finger angle
                            if 'angles' in analysis:
                                all_angles = []
                                for angles_list in analysis['angles'].values():
                                    all_angles.extend(angles_list)
                                if all_angles:
                                    avg_angle = sum(all_angles) / len(all_angles)
                                    cv2.putText(skeleton_3d, f"Avg Angle: {avg_angle:.0f}deg", (20, y_pos + 105),
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                        
                        right_panel = skeleton_3d
                    else:
                        # No hand detected - show placeholder
                        right_panel = np.zeros((right_panel_height, right_panel_width, 3), dtype=np.uint8)
                        right_panel[:] = (40, 40, 40)
                        cv2.putText(right_panel, "No Hands Detected", 
                                  (right_panel_width//2 - 150, right_panel_height//2),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
                        cv2.putText(right_panel, "Show both hands to the camera", 
                                  (right_panel_width//2 - 200, right_panel_height//2 + 40),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
                    
                    # Combine panels side by side with equal sizes
                    combined = np.hstack([image_resized, right_panel])
                    
                    # Add main title bar
                    title_height = 60
                    title_bar = np.zeros((title_height, combined.shape[1], 3), dtype=np.uint8)
                    title_bar[:] = (20, 20, 20)
                    
                    # Add gradient effect
                    for i in range(title_height):
                        intensity = int(100 + (155 * i / title_height))
                        title_bar[i, :] = (20, intensity//2, intensity)
                    
                    # Add hand count to title
                    hand_count = len(results.multi_hand_landmarks) if results and results.multi_hand_landmarks else 0
                    title_text = f"DUAL-HAND MUSICAL GESTURE RECOGNIZER ({hand_count}/2 HANDS)"
                    cv2.putText(title_bar, title_text, 
                              (combined.shape[1]//2 - 480, 40),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    # Stack title with content
                    final_display = np.vstack([title_bar, combined])
                    
                    cv2.imshow("Musical Gesture Recognition + Skeleton Analysis", final_display)
                    
                    # Handle key presses
                    key = cv2.waitKey(5) & 0xFF
                    if key == 27:  # ESC
                        break
                    elif key == ord('f') or key == ord('F'):
                        self.recognizer.show_fps = not self.recognizer.show_fps
                        print(f"  FPS display: {'ON' if self.recognizer.show_fps else 'OFF'}")
                    elif key == ord('3'):
                        self.show_3d = not self.show_3d
                        print(f"  3D skeleton: {'ON' if self.show_3d else 'OFF'}")
                    elif key == ord('p') or key == ord('P'):
                        self.show_panel = not self.show_panel
                        print(f"  Analysis panel: {'ON' if self.show_panel else 'OFF'}")
                    elif key == ord('s') or key == ord('S'):
                        self.show_skeleton_details = not self.show_skeleton_details
                        print(f"  Skeleton details: {'ON' if self.show_skeleton_details else 'OFF'}")
            
            cap.release()
            cv2.destroyAllWindows()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
        finally:
            self.synthesizer.cleanup()
            # Display summary
            print(self.statistics.get_summary())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Musical Hand Gesture Recognizer with Skeleton Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎵 Musical Gesture Recognition + Skeleton Analysis System 🦴

Examples:
  python app.py                  # Run with default camera (0)
  python app.py --camera 1       # Use camera device 1
  
Controls:
  ESC - Exit and show summary
  F   - Toggle FPS display
  3   - Toggle 3D skeleton visualization
  P   - Toggle analysis panel
  S   - Toggle skeleton details (angles, distances)
  
Features:
  ✓ Accurate gesture detection with stabilization
  ✓ Real-time musical note generation (C Major scale)
  ✓ Terminal feedback for each gesture
  ✓ Session statistics and summary
  ✓ 3D skeleton visualization with depth
  ✓ Joint angle measurements
  ✓ Fingertip distance tracking
  ✓ Real-time analysis panel
        """
    )
    
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera device ID (default: 0)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Musical Hand Gesture Recognizer + Skeleton Analysis v3.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create and run application
    try:
        app = MusicalGestureApp(camera_id=args.camera)
        app.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

