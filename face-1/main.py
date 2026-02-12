#!/usr/bin/env python3
"""
Todo App Entry Point
Memory-Based Console Todo Application

This module serves as the main entry point for the console-based todo application.
It creates and runs the CLI interface, handling startup and shutdown procedures.
"""
import sys
from src.todo_app.cli.interface import TodoAppCLI


def main():
    """
    Main application entry point

    Initializes the TodoAppCLI and starts the main application loop.
    Handles keyboard interrupts and unexpected errors gracefully.
    """
    try:
        cli = TodoAppCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye! Your tasks have been cleared.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()