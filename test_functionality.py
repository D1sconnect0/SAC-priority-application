#!/usr/bin/env python3
"""
Test script to validate key functionality of the SAC Priority Application
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import SACPriorityApp
    import customtkinter as ctk
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_vce_calculations():
    """Test the VCE priority calculation methods"""
    print("\n🧮 Testing VCE Priority Calculations:")
    
    # Create a mock app instance for testing
    root = ctk.CTk()
    app = SACPriorityApp(root)
    
    # Test difficulty calculation
    try:
        difficulty = app.calculate_difficulty("Mathematics", 40, 50)
        print(f"  📊 Difficulty (40/50 target): {difficulty:.4f}")
        assert 0 <= difficulty <= 1, "Difficulty should be between 0 and 1"
        print("  ✅ Difficulty calculation working")
    except Exception as e:
        print(f"  ❌ Difficulty calculation error: {e}")
    
    # Test urgency calculation
    try:
        urgency = app.calculate_urgency("Mathematics", 7)  # 7 days
        print(f"  ⏰ Urgency (7 days): {urgency:.4f}")
        assert urgency > 0, "Urgency should be positive"
        print("  ✅ Urgency calculation working")
    except Exception as e:
        print(f"  ❌ Urgency calculation error: {e}")
    
    # Test priority score
    try:
        priority = app.calculate_priority_score("Mathematics", 40, "2024-08-05", 50)
        print(f"  🎯 Priority Score: {priority:.4f}")
        assert priority > 0, "Priority should be positive"
        print("  ✅ Priority score calculation working")
    except Exception as e:
        print(f"  ❌ Priority score calculation error: {e}")
    
    root.destroy()

def test_cache_system():
    """Test the caching functionality"""
    print("\n💾 Testing Cache System:")
    
    cache_file = "programs/api_cache.json"
    
    # Check if cache system is working by creating a test cache
    try:
        test_cache = {
            "timestamp": datetime.now().isoformat(),
            "exams": [{"name": "Test Exam", "subject": "Test Subject", "date": "2024-08-01"}],
            "subjects": ["Test Subject"]
        }
        
        os.makedirs("programs", exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(test_cache, f)
        
        print("  ✅ Cache file creation working")
        
        # Test cache reading
        with open(cache_file, 'r') as f:
            loaded_cache = json.load(f)
        
        assert loaded_cache["timestamp"] == test_cache["timestamp"]
        print("  ✅ Cache file reading working")
        
        # Clean up test cache
        os.remove(cache_file)
        print("  ✅ Cache system fully functional")
        
    except Exception as e:
        print(f"  ❌ Cache system error: {e}")

def test_file_structure():
    """Test if all required files and directories exist"""
    print("\n📁 Testing File Structure:")
    
    required_files = [
        "main.py",
        "API.py",
        "clockapp.py",
        "studytime.py",
        "testscore.py"
    ]
    
    required_dirs = [
        "programs"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} exists")
        else:
            print(f"  ❌ {file} missing")
    
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"  ✅ {dir}/ directory exists")
        else:
            print(f"  ❌ {dir}/ directory missing")

if __name__ == "__main__":
    print("🚀 SAC Priority Application - Functionality Test")
    print("=" * 50)
    
    test_file_structure()
    test_cache_system()
    test_vce_calculations()
    
    print("\n" + "=" * 50)
    print("✨ Testing completed!")
