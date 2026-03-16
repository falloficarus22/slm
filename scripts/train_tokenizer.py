import argparse
import json
from pathlib import Path

from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers


def iter_lines(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            text = obj.get("text", "").strip()
            if text:
                yield text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file", type=str, default="data/processed/train.jsonl")
    parser.add_argument("--vocab-size", type=int, default=32000)
    parser.add_argument("--out-dir", type=str, default="artifacts/tokenizer")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.normalizer = normalizers.Sequence([normalizers.NFKC()])
    tok.pre_tokenzier = pre_tokenizers.ByteLevel(add_prefix_space=False)

    trainer = trainers.BpeTrainer(
        vocab_size=args.vocab_size,
        special_tokens=["[PAD]", "[UNK]", "[BOS]", "[EOS]"],
        show_progress=True,
    )

    tok.train_from_iterator(iter_lines(Path(args.train_file)), trainer=trainer)
    tok.save(str(out_dir / "tokenizer.json"))

    print(f"Tokenizer saved to {out_dir / 'tokenizer.json'}")


if __name__ == "__main__":
    main