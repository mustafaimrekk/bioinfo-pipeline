#!/usr/bin/env python3
"""
compute_read_stats.py
─────────────────────
Parses a FASTQ (plain or gzip-compressed) file and computes per-read:
  • GC content (%)
  • Read length (bp)
  • Mean read quality score (Phred)

Output: CSV with columns [read_id, gc_content, read_length, mean_quality]
"""

import argparse
import csv
import gzip
import math
import sys
from pathlib import Path


# ── Phred helpers ─────────────────────────────────────────────────────────────

def phred_char_to_score(char: str) -> int:
    """Convert a single ASCII quality character to its Phred score."""
    return ord(char) - 33


def mean_phred_from_string(qual_str: str) -> float:
    """
    Compute the mean Phred quality score from a quality string.

    Uses the correct probability-space average:
        Q_mean = -10 * log10( mean( 10^(-Q_i/10) ) )
    which avoids overestimating quality compared to a simple arithmetic mean.
    """
    if not qual_str:
        return 0.0
    error_probs = [10 ** (-phred_char_to_score(c) / 10.0) for c in qual_str]
    mean_error  = sum(error_probs) / len(error_probs)
    return -10.0 * math.log10(mean_error) if mean_error > 0 else 40.0


# ── GC content ────────────────────────────────────────────────────────────────

def gc_content(seq: str) -> float:
    """Return GC content as a percentage (0–100)."""
    seq_upper = seq.upper()
    gc = seq_upper.count("G") + seq_upper.count("C")
    return (gc / len(seq_upper) * 100.0) if seq_upper else 0.0


# ── FASTQ reader ─────────────────────────────────────────────────────────────

def open_fastq(path: Path):
    """Open a FASTQ file, handling optional gzip compression."""
    if path.suffix in (".gz", ".gzip"):
        return gzip.open(path, "rt")
    return open(path, "r")


def iter_fastq_records(path: Path):
    """
    Yield (read_id, sequence, quality_string) tuples for every read.
    Validates 4-line FASTQ structure; skips malformed records with a warning.
    """
    with open_fastq(path) as fh:
        while True:
            header  = fh.readline().rstrip()
            seq     = fh.readline().rstrip()
            plus    = fh.readline().rstrip()
            quality = fh.readline().rstrip()

            if not header:          # EOF
                break

            if not header.startswith("@"):
                print(f"[WARN] Unexpected header line: {header!r}", file=sys.stderr)
                continue

            if not plus.startswith("+"):
                print(f"[WARN] Missing '+' line after sequence; skipping.", file=sys.stderr)
                continue

            if len(seq) != len(quality):
                print(
                    f"[WARN] Sequence / quality length mismatch for {header!r}; skipping.",
                    file=sys.stderr,
                )
                continue

            read_id = header[1:].split()[0]   # strip '@' and take first token
            yield read_id, seq, quality


# ── Main ─────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",  "-i", required=True,  help="Input FASTQ (plain or .gz)")
    p.add_argument("--output", "-o", required=True,  help="Output CSV path")
    return p.parse_args()


def main():
    args   = parse_args()
    in_path  = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        sys.exit(f"[ERROR] Input file not found: {in_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["read_id", "gc_content", "read_length", "mean_quality"]
    n_reads = 0

    print(f"[INFO] Processing: {in_path}", file=sys.stderr)

    with open(out_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for read_id, seq, qual in iter_fastq_records(in_path):
            writer.writerow({
                "read_id":      read_id,
                "gc_content":   round(gc_content(seq), 4),
                "read_length":  len(seq),
                "mean_quality": round(mean_phred_from_string(qual), 4),
            })
            n_reads += 1
            if n_reads % 10_000 == 0:
                print(f"[INFO]   processed {n_reads:,} reads...", file=sys.stderr)

    print(f"[INFO] Done. {n_reads:,} reads written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
