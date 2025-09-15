#!/usr/bin/env python3
"""Entry point for PicSort executable."""
import sys
from src.cli.main import cli

if __name__ == '__main__':
    sys.exit(cli())