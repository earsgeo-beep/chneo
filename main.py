#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée de compatibilité pour CHNeoWave.
"""

import sys

from chneowave import main as launch_main


def main() -> int:
    return launch_main()


if __name__ == "__main__":
    sys.exit(main())
