import logging
import os

log_file = 'test_log.log'

print(f"Current working directory: {os.getcwd()}")
print(f"Attempting to log to: {os.path.abspath(log_file)}")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w'
)

logging.info("This is an info message.")
logging.debug("This is a debug message.")
logging.warning("This is a warning message.")

print(f"Logging configured. Check the file '{log_file}'.")

try:
    with open(log_file, 'r') as f:
        content = f.read()
        print("Log file content:")
        print(content)
except FileNotFoundError:
    print("Error: Log file was not created.")