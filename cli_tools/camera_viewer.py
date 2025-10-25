#!/usr/bin/env python3
"""
Bambu Lab Camera Viewer
=======================

View live camera feed from your Bambu Lab printer.
Supports both JPEG stream (P1/A1) and RTSP (X1) printers.
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import get_video_stream, JPEGFrameStream, RTSPStream, BambuClient


def view_jpeg_stream_opencv(stream, display_window=True, save_frames=False, output_dir=None):
    """
    View JPEG stream using OpenCV (if available).
    
    Args:
        stream: JPEGFrameStream instance
        display_window: Whether to display in window
        save_frames: Whether to save frames to disk
        output_dir: Directory to save frames
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("ERROR: OpenCV (cv2) not installed.")
        print("Install with: pip install opencv-python")
        return False
    
    if save_frames and output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Connecting to camera stream...")
    stream.connect()
    print("Connected! Press 'q' to quit.")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        for jpeg_data in stream.stream_frames():
            frame_count += 1
            
            # Decode JPEG
            nparr = np.frombuffer(jpeg_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                print("Warning: Failed to decode frame")
                continue
            
            # Calculate FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Add FPS overlay
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display
            if display_window:
                cv2.imshow('Bambu Lab Camera', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Save frame
            if save_frames and output_dir:
                filename = output_dir / f"frame_{frame_count:06d}.jpg"
                cv2.imwrite(str(filename), frame)
            
            # Print status
            if frame_count % 30 == 0:
                print(f"Frames: {frame_count}, FPS: {fps:.1f}")
    
    finally:
        stream.disconnect()
        if display_window:
            cv2.destroyAllWindows()
    
    return True


def view_jpeg_stream_pil(stream, display_window=True, save_frames=False, output_dir=None):
    """
    View JPEG stream using PIL/Pillow (if available).
    
    Args:
        stream: JPEGFrameStream instance
        display_window: Whether to display in window
        save_frames: Whether to save frames to disk
        output_dir: Directory to save frames
    """
    try:
        from PIL import Image
        import io
    except ImportError:
        print("ERROR: Pillow not installed.")
        print("Install with: pip install Pillow")
        return False
    
    if save_frames and output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Connecting to camera stream...")
    stream.connect()
    print("Connected! Press Ctrl+C to quit.")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        for jpeg_data in stream.stream_frames():
            frame_count += 1
            
            # Decode JPEG
            image = Image.open(io.BytesIO(jpeg_data))
            
            # Calculate FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Display (opens in default viewer)
            if display_window and frame_count == 1:
                print("Opening first frame in default viewer...")
                image.show()
            
            # Save frame
            if save_frames and output_dir:
                filename = output_dir / f"frame_{frame_count:06d}.jpg"
                image.save(filename)
            
            # Print status
            if frame_count % 30 == 0:
                print(f"Frames: {frame_count}, FPS: {fps:.1f}")
            
            # Limit to single frame if displaying
            if display_window and frame_count == 1:
                print("First frame displayed. Use --no-display to capture continuously.")
                break
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    finally:
        stream.disconnect()
    
    return True


def save_jpeg_frames(stream, output_dir, max_frames=None):
    """
    Save JPEG frames to disk without displaying.
    
    Args:
        stream: JPEGFrameStream instance
        output_dir: Directory to save frames
        max_frames: Maximum number of frames to capture (None = unlimited)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Connecting to camera stream...")
    stream.connect()
    print(f"Connected! Saving frames to {output_dir}")
    print("Press Ctrl+C to stop.")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        for jpeg_data in stream.stream_frames():
            frame_count += 1
            
            # Save frame
            filename = output_dir / f"frame_{frame_count:06d}.jpg"
            with open(filename, 'wb') as f:
                f.write(jpeg_data)
            
            # Print status
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            if frame_count % 30 == 0:
                print(f"Saved {frame_count} frames, FPS: {fps:.1f}")
            
            # Check max frames
            if max_frames and frame_count >= max_frames:
                print(f"Reached max frames: {max_frames}")
                break
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    finally:
        stream.disconnect()
        print(f"Total frames saved: {frame_count}")


def view_rtsp_stream(stream):
    """
    View RTSP stream (X1 series).
    
    Prints instructions for viewing with external players.
    """
    url = stream.get_stream_url()
    
    print("=" * 70)
    print("RTSP Stream URL:")
    print(url)
    print("=" * 70)
    print()
    print("To view the stream, use one of these methods:")
    print()
    print("1. VLC Media Player:")
    print(f"   vlc {url}")
    print()
    print("2. ffplay (from ffmpeg):")
    print(f"   ffplay -rtsp_transport tcp {url}")
    print()
    print("3. OpenCV in Python:")
    print(f"   import cv2")
    print(f"   cap = cv2.VideoCapture('{url}')")
    print(f"   while True:")
    print(f"       ret, frame = cap.read()")
    print(f"       if not ret: break")
    print(f"       cv2.imshow('Camera', frame)")
    print(f"       if cv2.waitKey(1) & 0xFF == ord('q'): break")
    print()
    print("4. Save to file with ffmpeg:")
    print(f"   ffmpeg -rtsp_transport tcp -i {url} -c copy output.mp4")
    print()


def get_printer_info(token):
    """Get printer information from cloud API."""
    try:
        client = BambuClient(token)
        devices = client.get_devices()
        
        if not devices:
            print("ERROR: No printers found in your account.")
            return None
        
        print("\nAvailable printers:")
        for idx, device in enumerate(devices, 1):
            name = device.get('name', 'Unknown')
            model = device.get('dev_product_name', 'Unknown')
            serial = device.get('dev_id', 'N/A')
            online = device.get('online', False)
            status = "Online" if online else "Offline"
            
            print(f"{idx}. {name} ({model}) - {status}")
            print(f"   Serial: {serial}")
            print(f"   Access Code: {device.get('dev_access_code', 'N/A')}")
        
        return devices
    
    except Exception as e:
        print(f"ERROR: Failed to get printer info: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="View camera feed from Bambu Lab printer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View camera from P1P printer
  python camera_viewer.py --ip 192.168.1.100 --code 12345678 --model P1P
  
  # Save frames to disk
  python camera_viewer.py --ip 192.168.1.100 --code 12345678 --save frames/
  
  # Auto-detect from cloud (requires token)
  python camera_viewer.py --token YOUR_TOKEN --device 0
  
  # Get RTSP URL for X1 series
  python camera_viewer.py --ip 192.168.1.100 --code 12345678 --model X1C
        """
    )
    
    # Connection options
    parser.add_argument('--ip', help='Printer IP address')
    parser.add_argument('--code', '--access-code', dest='code', help='Printer access code')
    parser.add_argument('--model', help='Printer model (X1C, P1P, A1, etc.)')
    
    # Cloud API options
    parser.add_argument('--token', help='Bambu Cloud token')
    parser.add_argument('--device', type=int, help='Device index from cloud (0-based)')
    
    # Display options
    parser.add_argument('--no-display', action='store_true', help='Do not display window')
    parser.add_argument('--save', metavar='DIR', help='Save frames to directory')
    parser.add_argument('--max-frames', type=int, help='Maximum frames to capture')
    parser.add_argument('--use-pil', action='store_true', help='Use PIL instead of OpenCV')
    
    args = parser.parse_args()
    
    # Get printer info from cloud if token provided
    if args.token:
        devices = get_printer_info(args.token)
        if not devices:
            return 1
        
        # Select device
        if args.device is not None:
            if args.device >= len(devices):
                print(f"ERROR: Device index {args.device} out of range (0-{len(devices)-1})")
                return 1
            device = devices[args.device]
        else:
            if len(devices) == 1:
                device = devices[0]
            else:
                print("\nMultiple printers found. Specify --device INDEX")
                return 1
        
        # Extract info
        args.ip = device.get('ip') or input("Enter printer IP address: ")
        args.code = device.get('dev_access_code')
        args.model = device.get('dev_product_name', 'Unknown')
        
        print(f"\nUsing printer: {device.get('name')} ({args.model})")
    
    # Validate required arguments
    if not args.ip or not args.code:
        print("ERROR: --ip and --code required (or use --token)")
        parser.print_help()
        return 1
    
    # Default model to P1P if not specified
    if not args.model:
        args.model = "P1P"
        print(f"Model not specified, defaulting to {args.model}")
    
    # Get stream handler
    stream = get_video_stream(args.ip, args.code, args.model)
    
    # Handle RTSP streams (X1 series)
    if isinstance(stream, RTSPStream):
        view_rtsp_stream(stream)
        return 0
    
    # Handle JPEG streams (P1/A1 series)
    if isinstance(stream, JPEGFrameStream):
        display = not args.no_display
        save_frames = args.save is not None
        
        # If saving only, use simple saver
        if save_frames and not display:
            save_jpeg_frames(stream, args.save, args.max_frames)
            return 0
        
        # Use appropriate viewer
        if args.use_pil:
            success = view_jpeg_stream_pil(stream, display, save_frames, args.save)
        else:
            success = view_jpeg_stream_opencv(stream, display, save_frames, args.save)
        
        return 0 if success else 1
    
    print(f"ERROR: Unknown stream type: {type(stream)}")
    return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
