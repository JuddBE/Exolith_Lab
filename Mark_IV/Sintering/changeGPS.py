import os
import sys
from dotenv import load_dotenv, find_dotenv, set_key

"""
Script used by desktop app to update whether the stand should use gps or not.
"""

# Load environment variables from .env file
env_file = find_dotenv()
load_dotenv(env_file)

def main():
    num_args = len(sys.argv)
    if num_args == 2:
        os.environ["useGPS"] = sys.argv[1]
    elif os.getenv("useGPS") == "True":
        os.environ["useGPS"] = "False"
    elif os.getenv("useGPS") == "False":
        os.environ["useGPS"] = "True"
    print(os.environ["useGPS"])
    set_key(env_file, "useGPS", os.environ["useGPS"])

if __name__ == "__main__":
    main()