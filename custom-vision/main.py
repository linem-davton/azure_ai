from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials

import os, time, uuid
from dotenv import load_dotenv

def main():
    
    # load configuration from environment variables
    training_endpoint = os.environ["TRAINING_ENDPOINT"]
    training_key = os.environ["TRAINING_KEY"]
    prediction_key = os.environ["PREDICTION_KEY"]
    prediction_endpoint = os.environ["PREDICTION_ENDPOINT"]

    project_id = os.environ["PROJECT_ID"]
    

    # Client Authentication
    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(training_endpoint, credentials)

    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    predictor = CustomVisionPredictionClient(prediction_endpoint, prediction_credentials)

    # get the project id of existing project in customvision.ai
    project = trainer.get_project(project_id)
    
    print(f'project with id {project.id} and name {project.name}')
    
    return trainer, predictor, project


def upload_images(trainer, project):
    
    # Reading configutation from environment variables
    # Expecting Directory to be in the following format IMAGE_DIRECTORY/CLASS_NAME/IMAGE_FILE
    TRAIN_DIRECTORY = os.environ["TRAIN_DIRECTORY"]
    TRAINING_CLASSES_NO = int(os.environ["TRAINING_CLASSES"])
    IM_CLASSES= [os.environ["CLASS_" + str(i)] for i in range(TRAINING_CLASSES_NO)]  

    # Adding tags to the project
    class_tags = [trainer.create_tag(project.id, im_class) for im_class in IM_CLASSES]
   
    # Uploading images to the project
    image_objects = []
    im_per_class = {}
    print("Adding images...")
    
    for im_class, class_tag in zip(IM_CLASSES, class_tags):
        print(f'uploading images for {im_class}')

        images_list = os.listdir(os.path.join(TRAIN_DIRECTORY, im_class))
        
        for image in images_list:
            with open(os.path.join(TRAIN_DIRECTORY, im_class, image), "rb") as image_contents:
                image_objects.append(ImageFileCreateEntry(name=image, contents=image_contents.read(), tag_ids=[class_tag.id]))
        
        im_per_class[im_class] = (len(images_list))
            
    upload_result = trainer.create_images_from_files(project.id, ImageFileCreateBatch(images=image_objects))
    
    print(im_per_class)

    # If the upload fails, we get an exception
    if not upload_result.is_batch_successful:
        print("Image batch upload failed.")
        for image in upload_result.images:
            print("Image status: ", image.status)

def train_project(trainer, project):
    prediction_resource_id = os.environ["PREDICTION_RESOURCE_ID"]

    print ("Training...")
    iteration = trainer.train_project(project.id)
    while (iteration.status != "Completed"):
        iteration = trainer.get_iteration(project.id, iteration.id)
        print ("Training status: " + iteration.status)
    time.sleep(30)
    # The iteration is now trained. Publish it to the project endpoint
    trainer.publish_iteration(project.id, iteration.id, "testmodel", prediction_resource_id)
    print ("Moeel published!")

def predict_image(predictor, project):
    # Verfiy the project is published via customvision.ai portal
    
    # Open the sample image and get back the prediction results.
    TEST_DIRECTORY = os.environ["TEST_DIRECTORY"]
    images_list = os.listdir(os.path.join(TEST_DIRECTORY))

    for image in images_list:
        with open(os.path.join(TEST_DIRECTORY, image), mode="rb") as test_data:
            # arguments are customvision.ai project id, model name that was published, image data
            results = predictor.classify_image(project.id, "testmodel", test_data.read())
        # Display the results.
        for prediction in results.predictions:
            print ("\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100))
        print("")

if __name__ == "__main__":
    # Loading environment variables
    print("Loading environment variables...")
    load_dotenv()

    trainer, predictor, project = main()
    #upload_images(trainer, project)
    #train_project(trainer, project)
    predict_image(predictor, project)
    print("Done!")