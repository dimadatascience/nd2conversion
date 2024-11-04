#!/usr/bin/env python

import os
import numpy as np
import re
import gc
<<<<<<< HEAD
from .io_tools import save_pickle, load_pickle
from .image_mapping import apply_mapping
=======
from ..io_tools import save_pickle, load_pickle
from ..image_mapping import apply_mapping
>>>>>>> develop
from concurrent.futures import ProcessPoolExecutor

def process_crop(mapping_file, moving_file, checkpoint_dir=None):
    """
    Apply affine and diffeomorphic mappings to a set of image crops and save/load results from checkpoints.

    Parameters:
        mapping_file (list): Path to diffeomorphic mapping file.
        moving_file (list): Path to moving crop file.
        checkpoint_dir (str): Directory to save/load checkpoint files.
    """
    match = re.search(r'\d+_\d+_\d+', moving_file)
    idx = match.group(0) # Get the first two indices

    checkpoint_path = os.path.join(checkpoint_dir, f'registered_split_{idx}.pkl')
    if not os.path.exists(checkpoint_path):
        moving_crop = load_pickle(moving_file)
        mapping = load_pickle(mapping_file)

        # Check for single valued array (such as white border)
        if not len(np.unique(moving_crop[1])) == 1:
        # Apply mappings
            save_pickle((moving_crop[0], apply_mapping(mapping, moving_crop[1], method='dipy')), checkpoint_path)
        else:
        # Return crop as is
            save_pickle(moving_crop[0], moving_crop[1])

        print(f"Saved checkpoint for i={moving_crop[0]}")
        
        del moving_crop, mapping
        gc.collect()        


def apply_mappings(mapping_files, moving_files, checkpoint_dir, max_workers=None):
    """
    Compute affine and diffeomorphic mappings between fixed and moving image crops in parallel.

    Parameters:
        mapping_files (list): List of filenames for the mapping.
        moving_files (list): List of filenames for the moving crops.
        checkpoint_dir (str): Directory to save/load checkpoint files.
        max_workers (int, optional): Maximum number of workers for parallel processing.

    Returns:
        list: List of mappings corresponding to each crop, or None for mismatched shapes.
    """
    if checkpoint_dir is not None:
        # Create checkpoint directory if it doesn't exist
        os.makedirs(checkpoint_dir, exist_ok=True)
        
    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each crop to be processed in parallel
        for moving_file, mapping_file,  in zip(moving_files, mapping_files):
            executor.submit(process_crop, mapping_file, moving_file, checkpoint_dir)

