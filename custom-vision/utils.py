import os
def get_images_from_dir(directory):
    # List to hold image file names
    images = []
    image_filenames = []

    # Supported image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

    # Iterate over the files in the directory
    for file in os.listdir(directory):
        # Check if the file is an image
        if os.path.splitext(file)[1].lower() in image_extensions:
            # Append the file name to the list, with directory
            images.append(os.path.join(directory, file))
            image_filenames.append(file)

    return images, image_filenames