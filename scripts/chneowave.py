#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper de lancement pour CHNeoWave depuis le répertoire scripts.
"""

import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from chneowave import main


if __name__ == "__main__":
    sys.exit(main())
