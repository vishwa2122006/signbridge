import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Must happen before any `app` import: tests never touch the real dataset/ folder.
os.environ["SIGNBRIDGE_DATA_DIR"] = tempfile.mkdtemp(prefix="signbridge-test-")
