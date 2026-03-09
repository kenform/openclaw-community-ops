#!/usr/bin/env python3
"""
Compatibility entrypoint for external coding assistants.

This project historically uses `bot.py` as the main pipeline runtime.
`pipeline.py` is provided as a stable alias so tools/docs can reference
`pipeline.py` without breaking existing deployment scripts.
"""

from bot import *  # re-export current pipeline symbols for inspection/tools
from bot import main as _main


if __name__ == "__main__":
    _main()
