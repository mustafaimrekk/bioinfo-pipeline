# Long-Read Sequencing QC Pipeline

A bioinformatics pipeline I built to perform quality control on long-read
sequencing data. It takes a raw FASTQ file, runs QC, calculates per-read
statistics, generates distribution plots, and uses the Claude API to
automatically write a plain-English interpretation of the results.

Built with Nextflow, Python, and the Anthropic Claude API.

---

## What it does

1. Runs **NanoPlot** — a QC tool designed specifically for long-read data
2. Calculates **GC content, read length, and quality score** for every read
3. Generates **distribution plots** showing the spread of those metrics
4. Uses **Claude AI** to write a plain-English summary of the results

---

## Requirements

- Nextflow >= 23.04
- Conda or Miniconda
- An Anthropic API key
  - Get one at https://console.anthropic.com
  - Set it: `export ANTHROPIC_API_KEY="your-key"`

---

## How to run

Clone the repo and run:
```bash
git clone https://github.com/mustafaimrekk/bioinfo-pipeline.git
cd bioinfo-pipeline

nextflow run main.nf \
    -profile conda \
    --input "data/your_reads.fastq.gz" \
    --outdir results
```

That's it. Nextflow handles the environment and runs everything in order.

---

## Output

| Folder | What's inside |
|---|---|
| `results/nanoplot/` | Full NanoPlot HTML report |
| `results/read_stats/` | Per-read CSV (GC content, length, quality) |
| `results/plots/` | 3-panel distribution figure (PNG) |
| `results/summary/` | Key statistics (mean, median, std, quartiles) |
| `results/report/` | AI-generated plain-English interpretation |

---

## Project structure
```
main.nf                   # Main Nextflow workflow (DSL2)
nextflow.config           # Pipeline config and profiles
modules/                  # One .nf file per pipeline step
scripts/                  # Python scripts for stats and plotting
config/environment.yml    # Conda environment (fully reproducible)
```

---

## Notes

- Tested with Oxford Nanopore data but should work with any long-read FASTQ
- The AI report step requires an Anthropic API key — the rest of the
  pipeline runs fine without it if you remove the GENERATE_REPORT step
- Test data can be generated with the snippet in `docs/`
