nextflow.enable.dsl = 2

include { NANOPLOT_QC        } from './modules/nanoplot_qc'
include { COMPUTE_READ_STATS } from './modules/compute_read_stats'
include { VISUALISE_STATS    } from './modules/visualise_stats'

workflow {
    // Create a channel from the input files
    reads_ch = Channel
        .fromPath(params.input, checkIfExists: true)
        .map { file ->
            def sample = file.baseName.replaceAll(/\.fastq$|\.fq$|\.fastq\.gz$|\.fq\.gz$/, '')
            tuple(sample, file)
        }

    // Run the three processes in order
    NANOPLOT_QC(reads_ch)
    COMPUTE_READ_STATS(reads_ch)
    VISUALISE_STATS(COMPUTE_READ_STATS.out.csv)
}

workflow.onComplete {
    log.info "Pipeline complete! Results in: ${params.outdir}"
}