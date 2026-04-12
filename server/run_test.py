#!/usr/bin/env python
import subprocess
import sys

result = subprocess.run([sys.executable, "test_cache.py"], cwd="d:\\bharatMail\\server")
sys.exit(result.returncode)
