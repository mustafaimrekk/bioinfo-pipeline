process VISUALISE_STATS {
    tag "$sample"
    publishDir "${params.outdir}/plots",   mode: 'copy', pattern: "*.png"
    publishDir "${params.outdir}/summary", mode: 'copy', pattern: "*.txt"

    input:
    tuple val(sample), path(csv)

    output:
    tuple val(sample), path("${sample}_distributions.png"), emit: plot
    tuple val(sample), path("${sample}_summary.txt"),       emit: summary

    script:
    """
    python ${projectDir}/scripts/visualise_distributions.py \
        --input   ${csv} \
        --output  ${sample}_distributions.png \
        --summary ${sample}_summary.txt \
        --sample  ${sample}
    """
}