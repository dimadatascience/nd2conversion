#!/usr/bin/env python

import argparse
import os
import numpy as np
import h5py
from utils.io import load_nd2, save_h5
from utils.io import save_chunks_h5

def main(args): 
    input_path = args.input_path.replace('.nd2', '.h5')
    filename = os.path.basename(input_path)
    dirname = os.path.basename(os.path.dirname(input_path))
    output_path = os.path.join(args.work_dir, 'data', 'input', 'image_registration', dirname, filename)

    if not os.path.exists(output_path):
        data = load_nd2(args.input_path)

        # convert_to_h5(src=args.input_path, dst=output_path)
        save_chunks_h5(data, output_path, args.crop_width_x, args.crop_width_y)

        #if args.delete_src:
        #    os.remove(args.input_path)

if __name__ == '__main__':
    # Set up argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Register images from input paths and save them to output paths.")
    parser.add_argument('--work-dir', type=str, required=True, 
                        help='Work directory of the process.')
    parser.add_argument('--input-path', type=str, required=True, 
                        help='Path to the input (moving) image.')
    parser.add_argument('--crop-width-x', required=True, type=int, 
                        help='Width of each crop.')
    parser.add_argument('--crop-width-y', required=True, type=int, 
                        help='Height of each crop.')
    parser.add_argument('--logs-dir', type=str, required=True, 
                        help='Directory to store log files.')
    #parser.add_argument('--delete-src', action='store_true', 
    #                    help='Delete intermediate files after processing.')
    args = parser.parse_args()
    main(args)
