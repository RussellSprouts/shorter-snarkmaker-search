import time

try:
    print("Program running... Press Ctrl+C to stop.")
    while True:
        # Long-running task
        time.sleep(1)
except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Performing graceful shutdown.")
    # Perform cleanup actions here (close files, sockets, etc.)
    print("Shutdown complete.")