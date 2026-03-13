from importlib import import_module

REQUIRED = [
    "torch",
    "transformers",
    "datasets",
    "tokenizers",
    "accelerate",
    "wandb",
    "numpy",
    "tqdm"
]

def main() -> int:
    missing = []
    for pkg in REQUIRED:
        try:
            import_module(pkg)
        except Exception:
            missing.append(pkg)

    if missing:
        print("Missing packages:", ", ".join(missing))
        return 1
    
    import torch
    print("Environment check passed.")
    print("Torch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())