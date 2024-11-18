#!/usr/bin/env python

import numpy as np
import gc
import argparse
import logging
import os
from utils import logging_config
from utils.misc import create_checkpoint_dirs
from utils.image_cropping import get_image_file_shape
from utils.image_cropping import get_padding_shape
from utils.image_cropping import crop_2d_array
from utils.image_cropping import get_crop_areas
from utils.image_mapping import compute_affine_mapping_cv2, apply_mapping
from utils.io import save_pickle, load_h5

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def binarize_image(image, thresh=None, alpha=1.5):
    if thresh == None:
        thresh = np.mean(image)
    return (image > thresh * alpha).astype('int8')

def affine_registration(input_path, fixed_image_path, current_registered_crops_dir, 
                        crop_width_x, crop_width_y, overlap_x, overlap_y, n_features=2000):
    """
    Registers moving and fixed images using an affine transformation and saves the registered image.

    Args:
        input_path (str): Path to the moving image.
        output_path (str): Path to save the registered image.
        fixed_image_path (str): Path to the fixed image used for registration.
        current_registered_crops_dir (str): Directory to store intermediate crops.
        crop (bool): Whether to compute affine mapping using a smaller region.
        crop_size (int): Size of the subregion for affine mapping.
        n_features (int): Number of features to use for the affine transformation.
    """
    # Get image shape and determine crop areas
    shape = get_image_file_shape(input_path)
    crop_areas = get_crop_areas(shape=shape, crop_width_x=crop_width_x, crop_width_y=crop_width_y, overlap_x=overlap_x, overlap_y=overlap_y)

    moving_image = load_h5(input_path, channels_to_load=[2])
    fixed_image = load_h5(fixed_image_path, channels_to_load=[2])

    logger.info(f'Computing affine transformation matrix.')
    matrix = compute_affine_mapping_cv2(fixed_image, moving_image, n_features)
    logger.info(f'Transformation computed successfully.')

    del moving_image, fixed_image
    gc.collect()
    
    # Apply the affine transformation to each crop and channel
    n_channels = 3
    for ch in range(n_channels):
        logger.debug(f"Loading moving image {input_path}")
        moving_image = load_h5(input_path, channels_to_load=[ch])
        moving_image = np.squeeze(moving_image)
        for idx, area in zip(crop_areas[0], crop_areas[1]):
            checkpoint_filename = os.path.join(current_registered_crops_dir, f'crop_{idx[0]}_{idx[1]}_{ch}.pkl')
            if not os.path.exists(checkpoint_filename):
                crop = crop_2d_array(
                    array=moving_image,
                    crop_areas=area
                )

                # crop = load_h5(input_path, area, [ch])
                # crop = np.squeeze(crop)

                logger.info(f'Applying transformation to moving crops.')
                crop = ((idx) + (ch,), apply_mapping(matrix, crop, 'cv2'))
                logger.info(f'Transformation applied successfully.')

                # Save the transformed crop
                save_pickle(crop, checkpoint_filename)
                logger.debug(f'Saved crop ({idx[0]}, {idx[1]}, {ch}) to {checkpoint_filename}')

                del crop
                gc.collect()

        del moving_image
        gc.collect()


def main(args):
    handler = logging.FileHandler(os.path.join(args.logs_dir, 'image_registration.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    input_path = args.input_path.replace('.nd2', '.h5')
    fixed_image_path = args.fixed_image_path.replace('.nd2', '.h5')
    
    filename_moving = os.path.basename(input_path) # Name of the output file 
    dirname_moving = os.path.basename(os.path.dirname(input_path)) # Name of the parent directory to output file

    filename_fixed = os.path.basename(fixed_image_path) # Name of the output file 
    dirname_fixed = os.path.basename(os.path.dirname(fixed_image_path)) # Name of the parent directory to output file

    input_path = os.path.join(args.input_dir, 'image_registration', dirname_moving, filename_moving)
    fixed_image_path = os.path.join(args.input_dir, 'image_registration', dirname_fixed, filename_fixed)

    print(f'INPUT PATH: {input_path}')
    print(f'FIXED IMAGE PATH: {fixed_image_path}')

    output_path = os.path.join(args.output_dir, 'image_registration', 'affine', dirname_moving, filename_moving) # Path to output file

    # Get image shape and determine crop areas
    mov_shape = get_image_file_shape(input_path)
    fixed_shape = get_image_file_shape(fixed_image_path)
    padding_shape = get_padding_shape(mov_shape, fixed_shape)
    crop_areas = get_crop_areas(
        shape=padding_shape, 
        crop_width_x=args.crop_width_x, crop_width_y=args.crop_width_y, 
        overlap_x=args.overlap_x, overlap_y=args.overlap_y
    )

    # Get checkpoint directories
    _, current_registered_crops_dir, _ = create_checkpoint_dirs(
        root_registered_crops_dir=args.registered_crops_dir, 
        moving_image_path=input_path,
        transformation='affine',
        makedirs=False
    )

    if os.path.exists(current_registered_crops_dir):
        n_registered_crops = len(os.listdir(current_registered_crops_dir))
    else:
        n_registered_crops = 0

    n_crops = len(crop_areas[0])
    
    if not os.path.exists(output_path) or n_registered_crops != n_crops:
        # Get checkpoint directories
        _, current_registered_crops_dir, _ = create_checkpoint_dirs(
            root_registered_crops_dir=args.registered_crops_dir, 
            moving_image_path=input_path,
            transformation='affine'
        )

        # Perform affine registration
        affine_registration(input_path, fixed_image_path, current_registered_crops_dir, 
                            args.crop_width_x, args.crop_width_y, args.overlap_x, args.overlap_y, args.n_features)
        

if __name__ == '__main__':
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Path to output work directory.')
    parser.add_argument('--input-dir', type=str, required=True, 
                        help='Path to input work directory.')
    parser.add_argument('--fixed-image-path', type=str, required=True, 
                        help='Path to the fixed image used for registration.')
    parser.add_argument('--registered-crops-dir', type=str, required=True, 
                        help='Directory to save intermediate registered crops.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--overlap-x', type=int, 
                        help='Overlap of each crop along the x-axis.')
    parser.add_argument('--overlap-y', type=int, 
                        help='Overlap of each crop along the y-axis.')
    parser.add_argument('--crop', action='store_true', 
                        help='Whether to compute the affine mapping using a smaller subregion of the image.')
    parser.add_argument('--crop-size', type=int, default=4000, 
                        help='Size of the subregion to use for affine mapping (if cropping is enabled).')
    parser.add_argument('--n-features', type=int, default=2000, 
                        help='Number of features to detect for computing the affine transformation.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Directory to store log files.')
    parser.add_argument('--delete-checkpoints', action='store_false', 
                        help='Delete intermediate files after processing.')
    args = parser.parse_args()
    main(args)