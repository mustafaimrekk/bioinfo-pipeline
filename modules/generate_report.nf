process GENERATE_REPORT {
    tag "$sample"
    publishDir "${params.outdir}/report", mode: 'copy'

    input:
    tuple val(sample), path(summary)

    output:
    tuple val(sample), path("${sample}_report.md"), emit: report

    script:
    """
    python ${projectDir}/scripts/generate_report.py \
        --summary ${summary} \
        --output  ${sample}_report.md \
        --sample  ${sample}
    """
}