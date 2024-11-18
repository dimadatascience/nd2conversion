#!/bin/bash

# Get user input
read -p "Enter work directory: " work_dir
read -p "Enter input directory (press Enter to use default): " input_dir
read -p "Enter output CSV path (press Enter to use default): " output_csv

# Set default values if not provided
if [[ -z "$input_dir" ]]; then
    input_dir="$work_dir/input/image_registration"
fi

if [[ -z "$output_csv" ]]; then
    output_csv="$work_dir/logs/io/sample_sheet.csv"
fi

# Create directory tree
sh 1_create_dir_tree.sh \
    --work-dir "$work_dir"

# Run Python script
python 2_generate_sample_sheet.py \
    --work-dir "$work_dir" \
    --input-dir "$input_dir" \
    --output-csv "$output_csv"

