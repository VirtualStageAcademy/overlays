import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FileFinder:
    def __init__(self, base_path):
        self.base_path = base_path

    def find_file(self, file_name):
        """Search for a file in the directory tree."""
        for root, dirs, files in os.walk(self.base_path):
            if file_name in files:
                return os.path.join(root, file_name)
        return None

if __name__ == "__main__":
    # Get base path from environment variable
    base_path = os.getenv("TECHHUB_PATH", "/path/to/your/TechHub")
    file_finder = FileFinder(base_path)

    # Example usage
    file_name = ".env"
    result = file_finder.find_file(file_name)
    if result:
        print(f"File found: {result}")
    else:
        print(f"{file_name} not found in {base_path}.")
