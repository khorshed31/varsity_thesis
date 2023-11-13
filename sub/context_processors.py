# your_app_name/context_processors.py

def user_info(request):
    user_info = {}
    if request.user.is_authenticated:
        user_info['first_name'] = request.user.first_name
        user_info['last_name'] = request.user.last_name
        user_info['email'] = request.user.email
        user_info['id'] = request.user.id
        user_info['is_staff'] = request.user.is_staff
        # Include any other user-related data you need
    return {'user_info': user_info}


def is_staff(request):
    # Initialize a dictionary to store user information
    user_data = {}

    if request.user.is_authenticated:
        user_data['is_staff'] = request.user.is_staff
    else:
        user_data['is_staff'] = False  # Default value for unauthenticated users

    return {'user_data': user_data}