from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
import numpy as np

# Import Computer Vision SDK
import azure.ai.vision as sdk

# helper functions
import utils



def main():
    global cv_client

    try:
        # Get Configuration Settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        # Image inputs
        image_files = utils.list_image_filenames('input_images') 
        modes = ['background_removal', 'foreground_matting']

        print(image_files)   
        # Authenticate Azure AI Vision client
        cv_client = sdk.VisionServiceOptions(ai_endpoint, ai_key)
        
        for image_file in image_files:
            # Analyze image
            AnalyzeImage(image_file, cv_client)
            
            # Generate thumbnail
            BackgroundForeground(image_file, cv_client, modes[0])
            BackgroundForeground(image_file, cv_client, modes[1])

    except Exception as ex:
        print(ex)


def AnalyzeImage(image_file, cv_client):
    print('\nAnalyzing', image_file)

    # Specify features to be retrieved
    analysis_options = sdk.ImageAnalysisOptions()

    features = analysis_options.features = (
        sdk.ImageAnalysisFeature.CAPTION |
        sdk.ImageAnalysisFeature.DENSE_CAPTIONS |
        sdk.ImageAnalysisFeature.TAGS |
        sdk.ImageAnalysisFeature.OBJECTS |
        sdk.ImageAnalysisFeature.PEOPLE
    )
    # Get image analysis
    image = sdk.VisionSource(image_file)

    image_analyzer = sdk.ImageAnalyzer(cv_client, image, analysis_options)

    result = image_analyzer.analyze()

    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        # Get image captions
        if result.caption is not None:
            print("\nCaption:")
            print(" Caption: '{}' (confidence: {:.2f}%)".format(result.caption.content, result.caption.confidence * 100))

        # Get image dense captions
        if result.dense_captions is not None:
            print("\nDense Captions:")
            for caption in result.dense_captions:
                print(" Caption: '{}' (confidence: {:.2f}%)".format(caption.content, caption.confidence * 100))

        # Get image tags
        if result.tags is not None:
            print("\nTags:")
            for tag in result.tags:
                print(" Tag: '{}' (confidence: {:.2f}%)".format(tag.name, tag.confidence * 100))

        # Get objects in the image (object detection)
        if result.objects is not None:
            print("\nObjects:")
            # Prepare image for drawing
            image = Image.open(image_file)
            #image = cv2.imread(image_file)

            fig = plt.figure(figsize=(image.width/100, image.height/100))
            plt.axis('off')
            draw = ImageDraw.Draw(image)
            color = 'cyan'
            for detected_object in result.objects:
                # Print object name
                print(" {} (confidence: {:.2f}%)".format(detected_object.name, detected_object.confidence * 100))
        
                # Draw object bounding box
                r = detected_object.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.w, r.y + r.h))
                draw.rectangle(bounding_box, outline=color, width=3)
                plt.annotate(detected_object.name,(r.x, r.y), backgroundcolor=color)

            # Save annotated image
            utils.save_output_image(image, image_file, 'objects')

        # Get people in the image
        if result.people is not None:
            # Get people in the image
            print("\nPeople in image:")

            # Prepare image for drawing
            image = Image.open(image_file)
            draw = ImageDraw.Draw(image)
            color = 'cyan'

            for detected_people in result.people:
                # Draw object bounding box
                r = detected_people.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.w, r.y + r.h))
                draw.rectangle(bounding_box, outline=color, width=3)

                # Return the confidence of the person detected
                #print(" {} (confidence: {:.2f}%)".format(detected_people.bounding_box, detected_people.confidence * 100))
            # Save annotated image
            utils.save_output_image(image, image_file, 'people')
    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print(" Analysis failed.")
        print("   Error reason: {}".format(error_details.reason))
        print("   Error code: {}".format(error_details.error_code))
        print("   Error message: {}".format(error_details.message))



def BackgroundForeground(image_file, cv_client, mode='background_removal'):
    # Remove the background from the image or generate a foreground matte
    print(f'\nRemove the background from the {image_file} or generate a foreground matte')

    image = sdk.VisionSource(image_file)

    analysis_options = sdk.ImageAnalysisOptions()

    # Set the image analysis segmentation mode to background or foreground
    if mode == 'background_removal':
        analysis_options.segmentation_mode = sdk.ImageSegmentationMode.BACKGROUND_REMOVAL
    
    else:
        analysis_options.segmentation_mode = sdk.ImageSegmentationMode.FOREGROUND_MATTING
    
    image_analyzer = sdk.ImageAnalyzer(cv_client, image, analysis_options)

    result = image_analyzer.analyze()

    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:

        image_buffer = result.segmentation_result.image_buffer
        print(" Segmentation result:")
        print("   Output image buffer size (bytes) = {}".format(len(image_buffer)))
        print("   Output image height = {}".format(result.segmentation_result.image_height))
        print("   Output image width = {}".format(result.segmentation_result.image_width))

        output_image_file = f'output_images/{utils.extract_filename(image_file)}-{mode}.jpg'
        with open(output_image_file, 'wb') as binary_file:
            binary_file.write(image_buffer)
            print("   File {} written to disk".format(output_image_file))
    
    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print(" Analysis failed.")
        print("   Error reason: {}".format(error_details.reason))
        print("   Error code: {}".format(error_details.error_code))
        print("   Error message: {}".format(error_details.message))
        print(" Did you set the computer vision endpoint and key?")


if __name__ == "__main__":
    main()
