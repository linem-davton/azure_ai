import os
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw

def list_image_filenames(directory):
    # List to hold image file names
    image_filenames = []

    # Supported image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

    # Iterate over the files in the directory
    for file in os.listdir(directory):
        # Check if the file is an image
        if os.path.splitext(file)[1].lower() in image_extensions:
            # Append the file name to the list, with directory
            image_filenames.append(os.path.join(directory, file))

    return image_filenames

def extract_filename(s):
    # Find the last occurrence of '/'
    slash_index = s.rfind('/') + 1  # Add 1 to start after the '/'

    # Find the occurrence of '.'
    dot_index = s.rfind('.')

    # Extract and return the substring
    return s[slash_index:dot_index]

def save_output_image(image, image_file, analysis_type):
    # Extract the file name
    filename = extract_filename(image_file)

    # Create the output directory
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)
    outputfile = os.path.join(output_dir, filename + '_' + analysis_type+'.jpg')
    
    # Save the image
    image.save(outputfile)
    print('  Results saved in', outputfile)