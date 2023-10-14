from typing import Counter
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
import cv2
import os
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
import tensorflow as tf
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import logging
from django.conf import settings
from django.contrib import messages
from .models import Report 
from .models import Exercise 
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def home(request):

    # Check if the user is authenticated
    if request.user.is_authenticated:
        user_info = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            # Include any other user-related data you need
        }
    else:
        user_info = None

    return render(request, 'home.html', {'user_info': user_info })

def therapy(request):

    records = Exercise.objects.all()

    return render(request, 'therapy.html', {'records': records})

def upload_video(request):

    records = Exercise.objects.all()
    return render(request, 'upload_video.html', {'records': records})

def classify_therapy(request):

    minutes = request.GET.get('minutes', '')
    seconds = request.GET.get('seconds', '')

    context = {
        'minutes': minutes,
        'seconds': seconds,
    }

    return render(request,'classify_therapy.html', context)

def web_cam(request):
    execrise_name = request.GET.get('execrise_name', '')
    execrise_type = request.GET.get('execrise_type', '')
    minutes = request.GET.get('minutes', '')
    seconds = request.GET.get('seconds', '')

    context = {
        'execrise_name': execrise_name,
        'execrise_type': execrise_type,
        'minutes': minutes,
        'seconds': seconds,
    }

    return render(request,'web_cam.html', context)


def results_page(request):
    analysis_result = request.session.get('analysis_result', None)
    execrise_type = request.session.get('therapy_name', None)
    execrise_name = request.session.get('execrise_name', None)

    if analysis_result is not None:
        # Remove the analysis_result from the session to clear it
        request.session.pop('analysis_result', None)
        request.session.pop('execrise_type', None)
        request.session.pop('execrise_name', None)

        # Render the results template and pass the analysis result
        return render(request, 'report.html', {'analysis_result': analysis_result, 'execrise_name' : execrise_name})
    else:
        # If analysis_result is not found in the session, show an error message
        messages.error(request, 'Analysis result not found.')
        return redirect('upload_video')   
    

# Define the exercise_to_model_mapping dictionary
exercise_to_model_mapping = {
    "e1": "home/physiotherapy_models/e1.h5",
    "e2": "home/physiotherapy_models/e2.h5",
    "e3": "home/physiotherapy_models/e3.h5",
    "e4": "home/physiotherapy_models/e4.h5",
    "e5": "home/physiotherapy_models/e5.h5",
    "e6": "home/physiotherapy_models/e6.h5",
    "e7": "home/physiotherapy_models/e7.h5",
    "e8": "home/physiotherapy_models/e8.h5",
}    
    

def load_pretrained_model(model_path):
    try:
        model = tf.keras.models.load_model(model_path)
        # Serialize the model's architecture and weights
        model_config = model.to_json()
        model_weights = model.get_weights()
        return model_config, model_weights
    except Exception as e:
        # Handle any exceptions that may occur during model loading
        print(f"Error loading the model: {str(e)}")
        return None, None 

# Load the pre-trained model
# model = load_pretrained_model('home/physiotherapy_models/e1.h5')    

 # Only for demonstration; use CSRF protection in production.
@csrf_exempt
def recorded_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video = request.FILES['video']
        execrise_type = request.POST.get('execrise_type', '') 
        execrise_name = request.POST.get('execrise_name', '') 
        fs = FileSystemStorage(location='media/')
        custom_name = 'video.webm'
        filename = fs.save(custom_name, video)
        
        #  # Ensure that the exercise_type is valid (i.e., it exists in your mapping)
        # if exercise_type not in exercise_to_model_mapping:
        #     return JsonResponse({'error': 'Invalid exercise type.'}, status=400)

         # Ensure that the exercise_type is valid (i.e., it exists in your mapping)
        if execrise_type not in exercise_to_model_mapping:
            return JsonResponse({'error': 'Invalid exercise type.'}, status=400)

        # Construct the file path to the uploaded video
        media_root = settings.MEDIA_ROOT
        video_file_path = os.path.join(media_root, filename)
        if video_file_path:
            # Inside your upload_video function
            analysis_result = process_video(video_file_path, execrise_type)

            # Delete the video file after processing
            os.remove(video_file_path)

            if 'error' in analysis_result:
                return JsonResponse({'error': analysis_result['error']}, status=500)
            else:
                # Format the predicted score with two decimal places
                formatted_score = '{:.2f}'.format(analysis_result['predicted_score'][0][0])
                # Store the analysis result in the session
                request.session['analysis_result'] = formatted_score
                request.session['execrise_type'] = execrise_type
                request.session['execrise_name'] = execrise_name

                return JsonResponse({'result': formatted_score})

    return JsonResponse({'message': 'Invalid request'}, status=400)

def process_video(video_file, exercise_type):
    sequence_length = 35  # Define the desired sequence length
    # Load the selected model based on the exercise type
    model_path = exercise_to_model_mapping.get(exercise_type)

    # Initialize the VideoCapture object to read from the video file.
    video_reader = cv2.VideoCapture(video_file)

    # Declare a list to store video frames we will extract.
    frames_list = []

    while True:
        # Read a frame.
        success, frame = video_reader.read()

        # Check if the frame is not read properly or we have enough frames.
        if not success or len(frames_list) >= sequence_length:
            break

        # Resize the frame to fixed dimensions.
        resized_frame = cv2.resize(frame, (128, 128))

        # Normalize the resized frame by dividing it by 255 so that each pixel value lies between 0 and 1.
        normalized_frame = resized_frame / 255

        # Append the pre-processed frame into the frames list.
        frames_list.append(normalized_frame)

    # Close the VideoCapture object.
    video_reader.release()

    # Check if we have enough frames for processing.
    if len(frames_list) < sequence_length:
        return {'error': 'Insufficient frames in the video.'}

    # Reshape the frames into the expected shape.
    frames_array = np.array(frames_list)
    frames_array = np.expand_dims(frames_array, axis=0)  # Add a batch dimension

    # Load the model architecture and weights
    model_config, model_weights = load_pretrained_model(model_path)

    if model_config is None or model_weights is None:
        return {'error': 'Failed to load the model.'}

    # Create a new model with the same architecture
    model = tf.keras.models.model_from_json(model_config)
    model.set_weights(model_weights)

    # Passing the pre-processed frames to the regression model and get the predicted score.
    predicted_score = model.predict(frames_array)

    return {'predicted_score': predicted_score.tolist()}  # Convert to JSON-serializable format

@csrf_exempt
def save_form_data(request):
    if request.method == 'POST':
        therapy_name = request.POST.get('therapy_name', '')
        user_id = request.POST.get('user_id', '')
        user_name = request.POST.get('user_name', '')
        result = request.POST.get('result', '')
        date = request.POST.get('date', '')

        # Create an instance of the Report model and save it to the database
        report_instance = Report(
            therapy_name=therapy_name,
            user_id=user_id,
            user_name=user_name,
            result=result,
            date=date
        )
        report_instance.save()

        return JsonResponse({'message': 'Data saved successfully'})
    else:
        return JsonResponse({'message': 'Invalid request method'}) 
    

def my_reports(request):
    user_data = Report.objects.filter(user_id=request.user.id)
    return render(request, 'my_reports.html', {'user_data': user_data})  

def delete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    try:
        # Attempt to delete the object
        report.delete()
        messages.success(request, 'Report deleted successfully')  # Set success message
    except Exception as e:
        messages.error(request, f'Error deleting report: {str(e)}', extra_tags='custom-error')  # Set error message with custom tag

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  # Redirect back to the previous page