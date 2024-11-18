#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PIPELINE WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { parse_csv } from './bin/utils/workflow.nf'       
include { convert_to_h5 } from './modules/local/image_conversion/main.nf'               
include { convert_to_ome_tiff } from './modules/local/image_conversion/main.nf'
include { affine_registration } from './modules/local/image_registration/main.nf' 
include { diffeomorphic_registration } from './modules/local/image_registration/main.nf'
include { apply_mappings } from './modules/local/image_registration/main.nf'
include { export_image_1 } from './modules/local/export_image/main.nf'
include { export_image_2 } from './modules/local/export_image/main.nf'
include { stack_dapi_crops } from './modules/local/image_stacking/main.nf'
include { pad_image } from './modules/local/image_padding/main.nf'
// include { stack_images } from './modules/local/image_stacking/main.nf'


workflow {

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PARSE CSV INPUT
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    parsed_lines = parse_csv(params.sample_sheet_path)

    // Prepare parameters from parsed CSV data
    params_parsed = parsed_lines.map { row ->
        tuple(
            row.patient_id,
            row.cycle_id,
            row.fixed_image_path,
            row.input_path,
            row.output_path
        )
    }


    // convert_to_h5(params_parsed)
    pad_image(params_parsed)
    affine_registration(pad_image.out)
    export_image_1(affine_registration.out)
    stack_dapi_crops(export_image_1.out)

    crops_data = stack_dapi_crops.out
            .map { it ->
                def patient_id = it[0]
                def cycle_id = it[1]
                def fixed_image_path = it[2]
                def input_path = it[3]
                def output_path = it[4]
                def crops_paths = it[5]  // Paths to *.pkl files
                
                return crops_paths.collect { crops_path ->                    
                    return [patient_id, cycle_id, fixed_image_path, input_path, output_path, crops_path]
                }
            } 
            .flatMap { it }

    diffeomorphic_registration(crops_data)

    unique_diffeo_out = diffeomorphic_registration.out
        .toList()
        .map { tuples ->
            tuples.unique() 
        }
        .flatMap()

    apply_mappings(unique_diffeo_out)

    export_image_2(apply_mappings.out)

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        IMAGE STACKING
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    // stack_images(export_image_2.out)

    /*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        CONVERSION TO OME.TIFF
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    */

    // input_conv = convert_to_ome_tiff(
    //     stack_images.out
    //         .combine(params_conv)
    // )
}
