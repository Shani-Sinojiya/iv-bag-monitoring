#!/usr/bin/env python3
"""
Setup script for IV Bag Monitoring System
Run this to install dependencies and verify the installation
"""

import subprocess
import sys
import importlib


def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing requirements...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def verify_installation():
    """Verify that all modules can be imported"""
    print("\nVerifying installation...")

    modules_to_test = [
        "sensors.hx711",
        "hardware.gpio_control",
        "api.client",
        "calibration.calibrator",
        "config.settings"
    ]

    all_good = True
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_good = False

    return all_good


def main():
    """Main setup function"""
    print("=" * 50)
    print("IV Bag Monitoring System - Setup")
    print("=" * 50)

    # Install requirements
    if not install_requirements():
        return False

    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed!")
        return False

    print("\n✓ Setup completed successfully!")
    print("\nTo run the system:")
    print("  python3 main.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
