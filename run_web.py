import subprocess
import sys

# Use pygbag's built-in server which handles CDN routing correctly
# The simple HTTP server doesn't route CDN requests properly
print("Starting pygbag development server...")
print("The game will open at http://localhost:8000")
print("Press Ctrl+C to stop.\n")

try:
    # Run pygbag without --build flag to start its built-in dev server
    subprocess.run([sys.executable, "-m", "pygbag", "main.py"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running pygbag: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nServer stopped.")
