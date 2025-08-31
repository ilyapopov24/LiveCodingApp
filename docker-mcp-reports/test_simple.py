#!/usr/bin/env python3
"""
Простой тестовый файл для проверки MCP Python Runner
"""

print("Hello from MCP Python Runner!")
print("This is a test file to verify the MCP server is working correctly.")

# Простое вычисление
result = 2 + 2
print(f"2 + 2 = {result}")

# Проверка импортов
import sys
import os
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

print("Test completed successfully!")



