import subprocess
import sys

styles = ["sarcaster", "flying_v", "sg", "les_paul", "jazzmaster"]

print("Starting render pipeline for all 5 styles...")
for style in styles:
    print(f"\n========================================\nRendering: {style}\n========================================")
    cmd = [
        sys.executable,
        "guitar_builder.py",
        style,
        "--render",
        "--uncut"
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Error: Rendering failed for {style} with return code {res.returncode}")
    else:
        print(f"Finished rendering for {style}")
        
print("\nAll renders completed successfully!")
