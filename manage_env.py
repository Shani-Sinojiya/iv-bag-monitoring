#!/usr/bin/env python3
"""
Environment management script for IoT Project
Helps copy and switch between different environment configurations
"""
import os
import shutil
import argparse


def copy_env_file(source: str, target: str = ".env"):
    """Copy an environment file"""
    if not os.path.exists(source):
        print(f"Error: Source file {source} does not exist")
        return False

    try:
        shutil.copy2(source, target)
        print(f"Successfully copied {source} to {target}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False


def list_env_files():
    """List available environment files"""
    env_files = []
    for file in os.listdir('.'):
        if file.startswith('.env'):
            env_files.append(file)
    return env_files


def main():
    parser = argparse.ArgumentParser(description="Manage environment files")
    parser.add_argument('command', choices=['list', 'use'],
                        help='Command to execute')
    parser.add_argument(
        '--env', help='Environment file to use (e.g., .env.production)')

    args = parser.parse_args()

    if args.command == 'list':
        env_files = list_env_files()
        print("Available environment files:")
        for file in env_files:
            print(f"  - {file}")

    elif args.command == 'use':
        if not args.env:
            print("Error: --env argument is required for 'use' command")
            return

        if copy_env_file(args.env):
            print(f"Now using {args.env} as .env")
            print("Restart your application to apply changes")


if __name__ == "__main__":
    main()
