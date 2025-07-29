#!/usr/bin/env python3
"""
Test script for target scores functionality
"""
import sys
import os
import csv

# Add the current directory to the path so we can import from main.py
sys.path.insert(0, '/home/harija/Downloads/SAC-priority-application')

# Test the load_target_scores function
def test_load_target_scores():
    # Import the function from main.py
    from main import load_target_scores, TARGET_SCORES_FILE
    
    print(f"Testing load_target_scores function...")
    print(f"Target scores file path: {TARGET_SCORES_FILE}")
    print(f"File exists: {os.path.exists(TARGET_SCORES_FILE)}")
    
    if os.path.exists(TARGET_SCORES_FILE):
        print(f"File contents:")
        with open(TARGET_SCORES_FILE, 'r') as f:
            print(f.read())
    
    # Load and display target scores
    target_scores = load_target_scores()
    print(f"Loaded target scores: {target_scores}")
    
    return target_scores

if __name__ == "__main__":
    test_load_target_scores()
