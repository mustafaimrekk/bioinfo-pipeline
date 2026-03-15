#!/usr/bin/env python3
"""
Reads the summary statistics text file and uses the Claude API
to generate a plain-English QC interpretation report.
"""

import argparse
import sys
from pathlib import Path
import anthropic


def generate_report(summary_text: str, sample: str) -> str:
    client = anthropic.Anthropic()

    prompt = f"""You are a bioinformatics assistant helping interpret
long-read sequencing QC results for a researcher.

Here are the quality control statistics for sample '{sample}':

{summary_text}

Write a short, clear report (around 300 words) for a molecular biology
professor who is not a bioinformatics expert. The report should:

1. Summarise what the key metrics mean in plain language
2. Assess whether the GC content looks normal (expected: 40-60%)
3. Assess whether the read lengths are suitable for long-read analysis
4. Assess whether the quality scores are acceptable (Q7+ is the
   standard threshold for Oxford Nanopore data)
5. Give a clear recommendation: should the data proceed to alignment,
   or does it need filtering or re-sequencing?

Be direct and specific. Refer to the actual numbers from the statistics.
Do not use jargon without explanation.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, help="Path to summary TXT file")
    parser.add_argument("--output",  required=True, help="Path to output markdown report")
    parser.add_argument("--sample",  required=True, help="Sample name")
    args = parser.parse_args()

    summary_path = Path(args.summary)
    if not summary_path.exists():
        sys.exit(f"Summary file not found: {summary_path}")

    summary_text = summary_path.read_text()
    print(f"Generating AI report for {args.sample}...")

    report = generate_report(summary_text, args.sample)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write as markdown with a header
    full_report = f"# QC Report — {args.sample}\n\n{report}\n"
    output_path.write_text(full_report)
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()