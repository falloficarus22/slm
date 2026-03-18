import argparse
import json
import re
from pathlib import Path

from datasets import Dataset, load_dataset

MATH_HINT_RE = re.compile(r"(\d|=|\+|-|\*|/|%|\bsolve\b|\bequation\b|\balgebra\b)", re.IGNORECASE)


def is_math_like(text: str) -> bool:
    if not text or len(text) < 10:
        return False
    return bool(MATH_HINT_RE.search(text))


def to_unified_text(example: dict) -> str:
    for key in ("text", "content", "body", "question"):
        if key in example and isinstance(example[key], str):
            return example[key].strip()
    print(f"Unrecognised keys: {list(example.keys())[:10]}")
    return ""


def write_jsonl(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="HuggingFaceTB/smollm-corpus")
    parser.add_argument("--config", type=str, default="cosmopedia-v2")
    parser.add_argument("--split", type=str, default="train")
    parser.add_argument("--max-samples", type=int, default=20000)
    parser.add_argument("--out-dir", type=str, default="data/processed")
    parser.add_argument("--scan-limit", type=int, default=20000)
    args = parser.parse_args()

    ds = load_dataset(args.dataset, args.config, split=args.split, streaming=True)
    texts = []
    scanned = 0
    for ex in ds:
        scanned += 1
        t = to_unified_text(ex)
        if is_math_like(t):
            texts.append({"text": t})
        if len(texts) >= args.max_samples or scanned >= args.scan_limit:
            break
        if scanned % 500 == 0:
            print(f"Scanned: {scanned}, kept: {len(texts)}")

    if not texts:
        raise RuntimeError(
            "No math like samples were collected. "
            "Check the dataset fields or relax the math filter."
        )
    
    filtered = Dataset.from_list(texts).shuffle(seed=42)
    n = len(filtered)
    n_train = int(0.8 * n)
    n_val = int(0.1 * n)

    train_rows = filtered.select(range(0, n_train))
    val_rows = filtered.select(range(n_train, n_train + n_val))
    test_rows = filtered.select(range(n_train + n_val, n))

    out_dir = Path(args.out_dir)
    write_jsonl(train_rows, out_dir / "train.jsonl")
    write_jsonl(val_rows, out_dir / "val.jsonl")
    write_jsonl(test_rows, out_dir / "test.jsonl")

    print(f"Filtered rows: {n}")
    print(f"train={len(train_rows)} val={len(val_rows)} test={len(test_rows)}")
    print(f"Wrote files to: {out_dir.resolve()}")


if __name__ == "__main__":
    main()