import traceback
from datetime import datetime

execution_trace = []
last_error = None

def add_trace(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    execution_trace.append(f"[{ts}] {msg}")
    print(f"TRACE: {msg}")

def set_error(err: str):
    global last_error
    last_error = err
