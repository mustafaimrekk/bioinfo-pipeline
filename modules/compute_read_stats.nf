process COMPUTE_READ_STATS {
    tag "$sample"
    publishDir "${params.outdir}/read_stats", mode: 'copy'

    input:
    tuple val(sample), path(fastq)

    output:
    tuple val(sample), path("${sample}_read_stats.csv"), emit: csv

    script:
    """
    python ${projectDir}/scripts/compute_read_stats.py \
        --input  ${fastq} \
        --output ${sample}_read_stats.csv
    """
}