#!/usr/bin/env python

import nd2
import pickle
import h5py
import numpy as np
from typing import Tuple
from math import ceil

"""
Pickle
"""
def save_pickle(object, path):
    # Open a file in binary write mode
    with open(path, 'wb') as file:
        # Serialize the object and write it to the file
        pickle.dump(object, file)

def load_pickle(path):
    # Open the file in binary read mode
    with open(path, 'rb') as file:
    # Deserialize the object from the file
        loaded_data = pickle.load(file)

    return loaded_data

"""
h5
"""
def save_h5(data, path, chunks=None):
    # Save the NumPy array to an HDF5 file
    with h5py.File(path, 'w') as hdf5_file:
        hdf5_file.create_dataset('dataset', data=data, chunks=chunks)
        hdf5_file.flush()

def save_chunks_h5(
    array: np.ndarray,
    output_path: str,
    crop_width_x: int,
    crop_width_y: int,
    verbose: bool = True
) -> Tuple[int, int]:
    """
    Saves a large numpy array to a new HDF5 file in chunks.

    Parameters
    ----------
    array : np.ndarray
        The input array to save. Must be 3-dimensional (height, width, channels).
    output_path : str
        The path to the output HDF5 file.
    crop_width_x : int
        The height of each chunk. Must be positive.
    crop_width_y : int
        The width of each chunk. Must be positive.
    verbose : bool, optional
        Whether to print progress information. Default is True.

    Returns
    -------
    Tuple[int, int]
        Number of chunks in x and y dimensions

    Examples
    --------
    >>> array = np.random.rand(48759, 37641, 3)  # Irregular shape
    >>> n_chunks_x, n_chunks_y = save_chunks_h5(array, "output.h5", 1000, 1000)
    >>> print(f"Created {n_chunks_x * n_chunks_y} chunks total")
    """
    if array.ndim != 3:
        raise ValueError(f"Expected 3D array, got {array.ndim}D")
    
    if crop_width_x <= 0 or crop_width_y <= 0:
        raise ValueError("Crop sizes must be positive")

    # Get the shape of the array
    n, m, c = array.shape

    # Calculate number of chunks in each dimension
    n_chunks_x = ceil(n / crop_width_x)
    n_chunks_y = ceil(m / crop_width_y)
    total_chunks = n_chunks_x * n_chunks_y

    if verbose:
        print(f"Array shape: {array.shape}")
        print(f"Number of chunks: {n_chunks_x} x {n_chunks_y} = {total_chunks}")
        print(f"Chunk size: {crop_width_x} x {crop_width_y}")
        print(f"Last chunk sizes: {n % crop_width_x} x {m % crop_width_y}")
        print(f"Estimated chunk sizes in MB: "
              f"{(crop_width_x * crop_width_y * c * array.dtype.itemsize) / (1024*1024):.2f}")

    try:
        with h5py.File(output_path, "w") as h5file:
            # Create a dataset with chunked storage
            dataset = h5file.create_dataset(
                name="dataset",
                shape=(n, m, c),
                dtype=array.dtype,
                chunks=(min(crop_width_x, n), min(crop_width_y, m), c)
            )

            chunks_processed = 0
            for start_row in range(0, n, crop_width_x):
                for start_col in range(0, m, crop_width_y):
                    # Calculate chunk boundaries
                    end_row = min(start_row + crop_width_x, n)
                    end_col = min(start_col + crop_width_y, m)

                    # Calculate current chunk size
                    current_chunk_size = (end_row - start_row) * (end_col - start_col) * c
                    current_chunk_mb = (current_chunk_size * array.dtype.itemsize) / (1024*1024)

                    # Extract and write chunk
                    chunk = array[start_row:end_row, start_col:end_col, :]
                    dataset[start_row:end_row, start_col:end_col, :] = chunk

                    chunks_processed += 1
                    if verbose:
                        print(f"Saved chunk {chunks_processed}/{total_chunks}: "
                              f"({start_row}:{end_row}, {start_col}:{end_col}) "
                              f"Size: {current_chunk_mb:.2f}MB "
                              f"Progress: {(chunks_processed/total_chunks)*100:.1f}%")

            return n_chunks_x, n_chunks_y

    except IOError as e:
        raise IOError(f"Error writing to file {output_path}: {str(e)}")

        
def load_h5(path, loading_region=None, channels_to_load=None):
    with h5py.File(path, 'r') as hdf5_file:
        dataset = hdf5_file['dataset']
        
        # Select region to load if loading_region is provided
        if loading_region is not None:
            start_row, end_row, start_col, end_col = loading_region
            data = dataset[start_col:end_col, start_row:end_row, :]
        else:
            data = dataset[:, :, :]
        
        # Select channels if channels_to_load is provided
        if channels_to_load is not None:
            data = data[:, :, channels_to_load]

    return data

"""
nd2
"""
def load_nd2(file_path):
    """
    Read an ND2 file and return the image array.
    
    Parameters:
    file_path (str): Path to the ND2 file
    
    Returns:
    numpy.ndarray: Image data
    """
    with nd2.ND2File(file_path) as nd2_file:
        data = nd2_file.asarray()
        data = data.transpose((1, 2, 0))
        
    return data
