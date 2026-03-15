process NANOPLOT_QC {
    tag "$sample"
    publishDir "${params.outdir}/nanoplot/${sample}", mode: 'copy'

    input:
    tuple val(sample), path(fastq)

    output:
    tuple val(sample), path("NanoPlot-report.html"), emit: report
    tuple val(sample), path("NanoStats.txt"),        emit: stats

    script:
    """
    NanoPlot \
        --fastq ${fastq} \
        --outdir . \
        --plots dot \
        --N50 \
        --threads ${task.cpus}
    """
}