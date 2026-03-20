import argparse
import json
from pathlib import Path

from datasets import load_dataset


def format_gsm8k(example: dict) -> dict:
    question = example["question"].strip()
    answer = example["answer"].strip()
    text = (
        "### Problem:\n"
        f"{question}\n\n"
        "### Solution:\n"
        f"{answer}\n"
    )
    return {"text": text}


def write_jsonl(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=str, default="data/processed")
    args = parser.parse_args()

    train_ds = load_dataset("openai/gsm8k", "main", split="train")
    test_ds = load_dataset("openai/gsm8k", "main", split="test")

    train_rows = [format_gsm8k(ex) for ex in train_ds]
    test_rows = [format_gsm8k(ex) for ex in test_ds]

    val_size = min(1000, max(1, len(train_rows) // 10))
    val_rows = train_rows[:val_size]
    final_train_rows = train_rows[val_size:]

    out_dir = Path(args.out_dir)
    write_jsonl(final_train_rows, out_dir / "train.jsonl")
    write_jsonl(val_rows, out_dir / "val.jsonl")
    write_jsonl(test_rows, out_dir / "test.jsonl")

    print(f"train={len(final_train_rows)} val={len(val_rows)} test={len(test_rows)}")
    print(f"Wrote to: {out_dir.resolve()}")

if __name__ == "__main__":
    main()