/*
    Register images with respect to a predefined fixed image
*/

process affine_registration {
    cpus 2
    memory "40G"
    publishDir "${params.registered_crops_dir}", mode: "copy"
    conda '/hpcnfs/scratch/DIMA/chiodin/miniconda3'
    // container "docker://tuoprofilo/toolname:versione"
    tag "registration_1"
    
    input:
    tuple val(patient_id),
        val(cycle_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path)

    output:
    tuple val(patient_id),
        val(cycle_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path)

    script:
    """
    if [ "${input_path}" != "${fixed_image_path}" ]; then
        affine_registration.py \
            --input-path "${input_path}" \
            --output-dir "${params.output_dir_reg}" \
            --fixed-image-path "${fixed_image_path}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --crop-width-x "${params.crop_width_x}" \
            --crop-width-y "${params.crop_width_y}" \
            --overlap-x "${params.overlap_x}" \
            --overlap-y "${params.overlap_y}" \
            --logs-dir "${params.logs_dir}" 
    fi
    """
}

process diffeomorphic_registration {
    cpus 2
    memory "5G"
    publishDir "${params.mappings_dir}", mode: "copy"
    conda '/hpcnfs/scratch/DIMA/chiodin/miniconda3'
    // container "docker://tuoprofilo/toolname:versione"
    tag "registration_2"
    
    input:
    tuple val(patient_id),
        val(cycle_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path),
        path(crops_path)
    
    output:
    tuple val(patient_id),
        val(cycle_id), 
        val(fixed_image_path),
        val(input_path),
        val(output_path)
        //,path("mapping*pkl")

    script:
    """
    if [ "${input_path}" != "${fixed_image_path}" ]; then
        diffeomorphic_registration.py \
            --input-path "${input_path}" \
            --output-dir "${params.output_dir_reg}" \
            --crops-path "${crops_path}" \
            --mappings-dir "${params.mappings_dir}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --logs-dir "${params.logs_dir}"     
    fi
    """
}

process apply_mappings {
    cpus 20
    memory "40G"
    publishDir "${params.registered_crops_dir}", mode: "copy"
    conda '/hpcnfs/scratch/DIMA/chiodin/miniconda3'
    // container "docker://tuoprofilo/toolname:versione"
    tag "apply"
    
    input:
    tuple val(patient_id),
        val(cycle_id),
        val(fixed_image_path),
        val(input_path),
        val(output_path)
    
    output:
    tuple val(patient_id),
        val(cycle_id), 
        val(fixed_image_path),
        val(input_path),
        val(output_path)

    script:
    """
    if [ "${input_path}" != "${fixed_image_path}" ]; then
        apply_mappings.py \
            --input-path "${input_path}" \
            --output-dir "${params.output_dir_reg}" \
            --crops-dir-moving "${params.crops_dir_moving}" \
            --mappings-dir "${params.mappings_dir}" \
            --registered-crops-dir "${params.registered_crops_dir}" \
            --max-workers "${params.max_workers}" \
            --logs-dir "${params.logs_dir}"     
    fi
    """
}