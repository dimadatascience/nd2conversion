#!/usr/bin/env python

import argparse
import os 
import logging
from skimage.io import imread 
from utils.image_cropping import crop_2d_array_grid
from utils.wrappers.create_checkpoint_dirs import create_checkpoint_dirs
# from utils.wrappers.compute_mappings import compute_mappings
from utils.wrappers.compute_mappings_parallel import compute_mappings
from utils.image_mapping import compute_affine_mapping_cv2, apply_mapping
from utils.wrappers.apply_mappings import apply_mappings
from utils.wrappers.export_image import export_image
from utils.empty_folder import empty_folder
from utils import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def register_images(input_path, output_path, fixed_image_path, 
                    mappings_dir, registered_crops_dir,  
                    crop_width_x, crop_width_y, overlap_x, overlap_y, 
                    delete_checkpoints, max_workers):
    logger.info(f'Output path: {output_path}')
    fixed_image = imread(fixed_image_path)
    moving_image = imread(input_path)

    logger.debug(f"Overlap X: {overlap_x}")
    logger.debug(f"Overlap Y: {overlap_y}")

    affine_mapping = compute_affine_mapping_cv2(fixed_image, moving_image)
    affine_reg_image = apply_mapping(affine_mapping, moving_image, method='cv2')

    fixed_crops = crop_2d_array_grid(fixed_image, crop_width_x, crop_width_y, overlap_x, overlap_y)
    moving_crops = crop_2d_array_grid(affine_reg_image, crop_width_x, crop_width_y, overlap_x, overlap_y)

    current_mappings_dir, current_registered_crops_dir = create_checkpoint_dirs(mappings_dir, registered_crops_dir, input_path)
    mappings = compute_mappings(fixed_crops=fixed_crops, moving_crops=moving_crops, checkpoint_dir=current_mappings_dir, max_workers=max_workers)
    registered_crops = apply_mappings(mappings=mappings, moving_crops=moving_crops, checkpoint_dir=current_registered_crops_dir)
    export_image(registered_crops, overlap_x, overlap_y, output_path)
    logger.info(f'Image {input_path} processed successfully.')

    if delete_checkpoints:
        empty_folder(current_mappings_dir)
        logger.info(f'Content deleted successfully: {current_mappings_dir}')
        empty_folder(current_registered_crops_dir)
        logger.info(f'Content deleted successfully: {current_registered_crops_dir}')

def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    register_images(args.input_path, args.output_path, args.fixed_image_path,
                    args.mappings_dir, args.registered_crops_dir, 
                    args.crop_width_x, args.crop_width_y, 
                    args.overlap_x, args.overlap_y, 
                    args.delete_checkpoints, args.max_workers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to input images.')
    parser.add_argument('--output-path', type=str, required=True, 
                        help='Path to registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to fixed image')
    parser.add_argument('--mappings-dir', type=str, required=True, 
                        help='Root directory to save mappings.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Root directory to save registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Crop width.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Crop height.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along x axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along y axis.')
    parser.add_argument('--max-workers', type=int, 
                        help='Maximum number of CPUs used by the process.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete image mappings and registered crops files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to directory where log files will be stored.')
    args = parser.parse_args()
    
    main(args)