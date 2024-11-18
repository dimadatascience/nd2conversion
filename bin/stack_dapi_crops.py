#!/usr/bin/env python

import argparse
import os 
import logging
import gc
import re
from utils.io import load_pickle, save_pickle
from utils import logging_config
from utils.image_cropping import crop_image_channels
from utils.misc import get_crops_dir

# Set up logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def stack_dapi_crops(input_path, fixed_image_path, current_crops_dir_fixed, current_crops_dir_moving):
    """
    Performs diffeomorphic registration between fixed and moving image crops.

    Args:
        current_crops_dir_fixed (str): Directory containing fixed image crops.
        current_crops_dir_moving (str): Directory containing moving image crops.
    """
    whole_slide_id_moving = os.path.basename(input_path).split('.')[0]
    whole_slide_id_fixed = os.path.basename(fixed_image_path).split('.')[0]

    if whole_slide_id_fixed != whole_slide_id_moving:
        # List of files in each directory
        crop_files = sorted([os.path.join(current_crops_dir_fixed, file) for file in os.listdir(current_crops_dir_fixed)])

        # Extract indices
        indices = [tuple(map(int, re.search(r'\d+_\d+_\d+', filename).group(0).split('_'))) for filename in crop_files]
        indices_dapi = [index for index in indices if index[2] == 2]

        for idx in indices_dapi:
            crop_filename = f"crop_{idx[0]}_{idx[1]}_{idx[2]}.pkl"

            fixed_file = os.path.join(current_crops_dir_fixed, crop_filename)
            moving_file = os.path.join(current_crops_dir_moving, crop_filename)
            
            fixed = load_pickle(fixed_file)
            moving = load_pickle(moving_file)

            if fixed[1].shape == moving[1].shape:
                save_pickle((idx, fixed[1], moving[1]), f"{whole_slide_id_moving}_{idx[0]}_{idx[1]}_{idx[2]}.pkl")
            else:
                logger.error(f"Fixed crop and moving crop should be the same size. Fixed crop shape: {fixed[1].shape}, Moving crop shape: {moving[1].shape}")
            
            del fixed, moving
            gc.collect()

        # # Filter the files that end with '2.pkl'
        # fixed_files = sorted([os.path.join(current_crops_dir_fixed, file) for file in os.listdir(current_crops_dir_fixed)])
        # moving_files = sorted([os.path.join(current_crops_dir_moving, file) for file in os.listdir(current_crops_dir_moving)])
        # fixed_files_dapi = [f for f in fixed_files if f.endswith('_2.pkl')]   
        # moving_files_dapi = [f for f in moving_files if f.endswith('_2.pkl')]
        # for fixed_file, moving_file in zip(fixed_files_dapi, moving_files_dapi):
        #     fixed = load_pickle(fixed_file)
        #     moving = load_pickle(moving_file)
        # 
        #     idx, fixed = fixed[0], fixed[1]
        #     _, moving = moving[0], moving[1]
        # 
        #     if fixed.shape == moving.shape:
        #         save_pickle((idx, fixed, moving), f"{whole_slide_id_moving}_{idx[0]}_{idx[1]}_{idx[2]}.pkl")
        #                 
        #     del fixed, moving
        #     gc.collect()

    else:
        save_pickle(0, f"{whole_slide_id_fixed}.pkl")

def main(args):
    # Set up logging to a file
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_path = args.input_path.replace('.nd2', '.h5')
    filename = os.path.basename(input_path) # Name of the output file 
    dirname = os.path.basename(os.path.dirname(input_path)) # Name of the parent directory to output file
    input_path = os.path.join(args.output_dir, 'affine', dirname, filename) # Path to input file

    fixed_image_path = args.fixed_image_path.replace('.nd2', '.h5')

    # Create intermediate directories for crops
    current_crops_dir_fixed = get_crops_dir(fixed_image_path, args.crops_dir_fixed)
    current_crops_dir_moving = get_crops_dir(input_path, args.crops_dir_moving)

    if args.input_path != args.fixed_image_path:
        # Crop images and save them to the crops directories
        crop_image_channels(input_path, current_crops_dir_fixed, args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y)

    stack_dapi_crops(input_path, fixed_image_path, current_crops_dir_fixed, current_crops_dir_moving)

if __name__ == "__main__":
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to save the registered image.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--crops-dir-fixed', type=str, required=True,
                        help='Directory where fixed image crops will be saved.')
    parser.add_argument('--crops-dir-moving', type=str, required=True,
                        help='Directory where moving image crops will be saved.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along the x-axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along the y-axis.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete intermediate files after processing.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)
