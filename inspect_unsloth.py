import modal

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
    .pip_install(
        "torch==2.5.1",
        "transformers==4.48.3",
        "unsloth"
    )
)

app = modal.App("inspect-unsloth")

storage_volume = modal.Volume.from_name("bct-swarm-storage")

@app.function(image=image, volumes={"/workspace/data": storage_volume})
def print_file():
    filepath = "/usr/local/lib/python3.11/site-packages/unsloth/models/vision.py"
    with open(filepath, "r") as f:
        content = f.read()
    
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if "is_vlm" in line or "AutoModelForVision2Seq" in line or "AutoModelForImageTextToText" in line:
            print(f"--- MATCH AT LINE {idx+1} ---")
            start = max(0, idx - 5)
            end = min(len(lines), idx + 5)
            for j in range(start, end):
                print(f"{j+1}: {lines[j]}")



