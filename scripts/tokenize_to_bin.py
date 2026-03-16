import argparse
import json
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer


def read_texts(jsonl_path: Path):
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            text = obj.get("text", "").strip()
            if text:
                yield text

            
def encode_file(tokenizer: Tokenizer, inp: Path, out: Path):
    all_ids = []
    for text in read_texts(inp):
        ids = tokenizer.encode(text).ids
        all_ids.extend(ids + [3])
    arr = np.array(all_ids, dtype=np.uint16)
    out.parent.mkdir(parents=True, exist_ok=True)
    arr.tofile(out)
    print(f"{inp.name}: tokens={len(arr)} -> {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokenizer", type=str, default="artifacts/tokenizer/tokenizer.json")
    parser.add_argument("--in-dir", type=str, default="data/processed")
    parser.add_argument("--out-dir", type=str, default="data/tokenized")
    args = parser.parse_args()

    tok = Tokenizer.from_file(args.tokenizer)
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)

    for split in ("train", "val", "test"):
        encode_file(tok, in_dir / f"{split}.jsonl", out_dir / f"{split}.bin")


if __name__ == "__main__":
    main()