#!/usr/bin/env python3
"""
visualise_distributions.py
──────────────────────────
Reads the per-read stats CSV produced by compute_read_stats.py and generates:
  1. A 3-panel figure (GC content, Read Length, Mean Quality) saved as PNG
  2. A plain-text summary of key statistics for all three metrics

Usage:
    python visualise_distributions.py \
        --input  sample1_read_stats.csv \
        --output sample1_distributions.png \
        --summary sample1_summary.txt \
        --sample  sample1
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # non-interactive backend (works in containers)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec


# ── Colour palette ────────────────────────────────────────────────────────────
COLOURS = {
    "gc":      "#2196F3",   # blue
    "length":  "#4CAF50",   # green
    "quality": "#FF9800",   # orange
}

ALPHA = 0.80


# ── Summary statistics ────────────────────────────────────────────────────────

def summary_stats(series: pd.Series) -> dict:
    return {
        "n":      len(series),
        "mean":   series.mean(),
        "median": series.median(),
        "std":    series.std(),
        "min":    series.min(),
        "q25":    series.quantile(0.25),
        "q75":    series.quantile(0.75),
        "max":    series.max(),
    }


def write_summary(stats: dict, sample: str, path: Path):
    """Write a human-readable summary text file."""
    lines = [
        f"Read Statistics Summary — {sample}",
        "=" * 50,
        "",
    ]

    labels = {
        "gc":      ("GC Content (%)",          ""),
        "length":  ("Read Length (bp)",         ""),
        "quality": ("Mean Read Quality (Phred)", ""),
    }

    for key, (title, _) in labels.items():
        s = stats[key]
        lines += [
            f"{title}",
            f"  Reads   : {s['n']:,}",
            f"  Mean    : {s['mean']:.2f}",
            f"  Median  : {s['median']:.2f}",
            f"  Std Dev : {s['std']:.2f}",
            f"  Min     : {s['min']:.2f}",
            f"  Q25     : {s['q25']:.2f}",
            f"  Q75     : {s['q75']:.2f}",
            f"  Max     : {s['max']:.2f}",
            "",
        ]

    path.write_text("\n".join(lines))
    # Also print to stdout for pipeline log visibility
    print("\n".join(lines))


# ── Plotting ──────────────────────────────────────────────────────────────────

def add_stat_lines(ax, series, colour):
    """Overlay mean and median vertical lines on a histogram axis."""
    mean_val   = series.mean()
    median_val = series.median()
    ax.axvline(mean_val,   color="black",  linestyle="--", linewidth=1.2,
               label=f"Mean {mean_val:.1f}")
    ax.axvline(median_val, color="dimgray", linestyle=":",  linewidth=1.2,
               label=f"Median {median_val:.1f}")
    ax.legend(fontsize=8, framealpha=0.7)


def plot_gc(ax, gc_series):
    ax.hist(gc_series, bins=50, color=COLOURS["gc"], alpha=ALPHA, edgecolor="white", linewidth=0.3)
    add_stat_lines(ax, gc_series, COLOURS["gc"])
    ax.set_xlabel("GC Content (%)", fontsize=11)
    ax.set_ylabel("Number of Reads", fontsize=11)
    ax.set_title("GC Content Distribution", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))


def plot_lengths(ax, len_series):
    # Use log-scale bins so short and long reads are both visible
    min_len = max(len_series.min(), 1)
    max_len = len_series.max()
    bins = np.logspace(np.log10(min_len), np.log10(max_len), 60)

    ax.hist(len_series, bins=bins, color=COLOURS["length"], alpha=ALPHA,
            edgecolor="white", linewidth=0.3)
    add_stat_lines(ax, len_series, COLOURS["length"])
    ax.set_xscale("log")
    ax.set_xlabel("Read Length (bp, log scale)", fontsize=11)
    ax.set_ylabel("Number of Reads", fontsize=11)
    ax.set_title("Read Length Distribution", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))


def plot_quality(ax, qual_series):
    ax.hist(qual_series, bins=50, color=COLOURS["quality"], alpha=ALPHA,
            edgecolor="white", linewidth=0.3)
    add_stat_lines(ax, qual_series, COLOURS["quality"])
    # Shade common ONT quality thresholds
    ax.axvspan(0, 7,  alpha=0.06, color="red",   label="Q < 7 (low)")
    ax.axvspan(7, 10, alpha=0.06, color="yellow", label="Q 7–10 (moderate)")
    ax.axvspan(10, ax.get_xlim()[1] if ax.get_xlim()[1] > 10 else 40,
               alpha=0.06, color="green", label="Q ≥ 10 (high)")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=8, framealpha=0.7)
    ax.set_xlabel("Mean Phred Quality Score", fontsize=11)
    ax.set_ylabel("Number of Reads", fontsize=11)
    ax.set_title("Mean Read Quality Distribution", fontsize=13, fontweight="bold")


def make_figure(df: pd.DataFrame, sample: str, out_path: Path):
    fig = plt.figure(figsize=(16, 5))
    fig.suptitle(f"Long-Read QC — {sample}", fontsize=15, fontweight="bold", y=1.01)

    gs = GridSpec(1, 3, figure=fig, wspace=0.35)
    ax_gc  = fig.add_subplot(gs[0, 0])
    ax_len = fig.add_subplot(gs[0, 1])
    ax_qc  = fig.add_subplot(gs[0, 2])

    plot_gc(ax_gc,       df["gc_content"])
    plot_lengths(ax_len, df["read_length"])
    plot_quality(ax_qc,  df["mean_quality"])

    for ax in (ax_gc, ax_len, ax_qc):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3, linewidth=0.6)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Figure saved to {out_path}", file=sys.stderr)


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",   "-i", required=True, help="Input CSV from compute_read_stats.py")
    p.add_argument("--output",  "-o", required=True, help="Output PNG path")
    p.add_argument("--summary", "-s", required=True, help="Output summary TXT path")
    p.add_argument("--sample",        default="sample", help="Sample name for plot titles")
    return p.parse_args()


def main():
    args = parse_args()
    in_path  = Path(args.input)
    out_png  = Path(args.output)
    out_txt  = Path(args.summary)

    if not in_path.exists():
        sys.exit(f"[ERROR] Input CSV not found: {in_path}")

    print(f"[INFO] Reading {in_path}", file=sys.stderr)
    df = pd.read_csv(in_path)

    required = {"gc_content", "read_length", "mean_quality"}
    missing  = required - set(df.columns)
    if missing:
        sys.exit(f"[ERROR] Missing columns in CSV: {missing}")

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=list(required), inplace=True)

    if df.empty:
        sys.exit("[ERROR] No valid rows found after parsing.")

    stats = {
        "gc":      summary_stats(df["gc_content"]),
        "length":  summary_stats(df["read_length"]),
        "quality": summary_stats(df["mean_quality"]),
    }

    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_txt.parent.mkdir(parents=True, exist_ok=True)

    make_figure(df, args.sample, out_png)
    write_summary(stats, args.sample, out_txt)


if __name__ == "__main__":
    main()
