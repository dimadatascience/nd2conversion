#!/usr/bin/env python

import argparse
import os 
import logging
import numpy as np
import gc
from utils.io import load_nd2, save_chunks_h5
from utils import logging_config
from utils.image_cropping import zero_pad_array
from utils.image_cropping import get_image_file_shape
from pathlib import Path
from typing import List

# Set up logging configuration
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def list_files_recursive(directory: str, pattern: str = "*") -> List[Path]:
    """
    List all files in a directory and its subdirectories recursively.
    
    Args:
        directory (str): The root directory to start searching from
        pattern (str): Optional glob pattern to filter files (e.g., "*.txt", "*.py")
    
    Returns:
        List[Path]: List of Path objects for each file found
    """
    root_path = Path(directory)
    
    if not root_path.exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")
    
    if not root_path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a directory")
        
    # Use list comprehension to gather all files matching the pattern
    return [
        str(file_path) for file_path in root_path.rglob(pattern)
        if file_path.is_file()
    ]

def get_max_axis_value(paths, axis):
    shapes = [get_image_file_shape(path, format='.nd2') for path in paths]
    values = [shape[axis] for shape in shapes]

    return max(values)

def main(args):
    # Set up logging to a file
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_dir_reg = os.path.join(args.input_dir, 'image_registration')

    input_path = args.input_path.replace('.nd2', '.h5')
    filename = os.path.basename(input_path) # Name of the output file 
    dirname = os.path.basename(os.path.dirname(input_path)) # Name of the parent directory to output file

    output_path = os.path.join(input_dir_reg, dirname, filename) # Path to input file

    paths = list_files_recursive(input_dir_reg)
    paths = [path for path in paths if '.nd2' in path]
    paths = [path for path in paths if args.patient_id in path]

    if paths:
        padding_shape = []
        padding_shape.append(get_max_axis_value(paths, axis=0))
        padding_shape.append(get_max_axis_value(paths, axis=1))
        
        padding_shape = (padding_shape[0], padding_shape[1])

        if os.path.exists(output_path):
            image_shape = get_image_file_shape(output_path, format='.h5')

        if not os.path.exists(output_path) or image_shape[0] != padding_shape[0] or image_shape[1] != padding_shape[1]:
            n_channels = 3
            padded_images = []
            image = load_nd2(args.input_path)
            for ch in range(n_channels):
                padded_images.append(
                    zero_pad_array(
                        np.squeeze(image[:,:,ch]), 
                        padding_shape
                    )
                )
            
            del image
            gc.collect()

            save_chunks_h5(array=np.stack(padded_images, axis=-1), output_path=output_path, crop_width_x=args.crop_width_x, crop_width_y=args.crop_width_y)

            del padded_images
            gc.collect()

if __name__ == "__main__":
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--patient-id', type=str, required=True, 
                        help='ID of the current patient.')
    parser.add_argument('--input-dir', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--crop-width-x', required=True, type=int,
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Path to the directory where log files will be stored.')
    
    args = parser.parse_args()
    
    main(args)
