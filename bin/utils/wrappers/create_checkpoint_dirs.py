import os

def remove_file_extension(filename):
    while True:
        filename, ext = os.path.splitext(filename)
        if not ext:
            break
    return filename

def create_checkpoint_dirs(root_mappings_dir, root_registered_crops_dir, moving_image_path):
    filename = remove_file_extension(os.path.basename(moving_image_path))
    image_dir = os.path.basename(os.path.dirname(moving_image_path))

    mappings_dir = os.path.join(root_mappings_dir, image_dir)
    registered_crops_dir = os.path.join(root_registered_crops_dir, image_dir)
    current_mappings_dir = os.path.join(root_mappings_dir, image_dir, filename)
    current_registered_crops_dir = os.path.join(root_registered_crops_dir, image_dir, filename)

    if not os.path.exists(mappings_dir):
        os.makedirs(mappings_dir, exist_ok=True)

    if not os.path.exists(registered_crops_dir):
        os.makedirs(registered_crops_dir, exist_ok=True)

    if not os.path.exists(current_mappings_dir):
        os.makedirs(current_mappings_dir, exist_ok=True)
    
    if not os.path.exists(current_registered_crops_dir):
        os.makedirs(current_registered_crops_dir, exist_ok=True)

    return current_mappings_dir, current_registered_crops_dir