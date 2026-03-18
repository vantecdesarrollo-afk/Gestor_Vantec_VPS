import traceback
import sys

try:
    import src.main
    print("SUCCESS")
except Exception as e:
    print(traceback.format_exc())
