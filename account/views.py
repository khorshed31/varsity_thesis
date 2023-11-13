from django.shortcuts import render,redirect,reverse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import AssignedPatient
from django.http import JsonResponse
from home.models import Report 

# Create your views here.
def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        userName = request.POST['username']
        is_patient = request.POST['is_patient']
        # userRole = request.POST['role']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        if password == cpassword:
            if User.objects.filter(username=userName).exists():
                messages.error(request, 'Username already exist!')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exist!')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=userName, password=password, email=email, is_staff=is_patient)
                user.save()

                 # Assign a physiotherapist to the patient
                if is_patient == '0':
                    physiotherapist_id = request.POST['physiotherapist_id']
                    # physiotherapist = User.objects.get(pk=physiotherapist_id)
                    assignment = AssignedPatient(user_id=user.id, physiotherapist_id=physiotherapist_id, is_active=False)
                    assignment.save()
                return redirect('signin')
        else:
            messages.error(request, 'Password and confirm password doesnt match')

    physiotherapists = User.objects.filter(is_staff = 1)
    return render(request, 'account/signup.html', {'physiotherapists': physiotherapists})        

def signin(request):
    if request.method == 'POST':
        userName=request.POST['username']
        password =request.POST['password']
        user = authenticate(request,username=userName,password=password)
        user.save()
        
        if user is not None:
            login(request,user)
            if user.is_staff == 0:
                return redirect(reverse('home'))
            else:
                return redirect(reverse('physiotherapist'))
        else:
            messages.error(request, 'Invalid Username or Password!')
    else:
        return render(request,'index.html')
    
def signout(request):
    logout(request)
    messages.success(request, 'Successfully Logout!!.')
    return redirect('signin')

def physiotherapist(request):
    if request.user.is_authenticated:
        # Get the currently authenticated user (assumed to be a physiotherapist)
        physiotherapist = request.user
        # Filter the AssignedPatient objects to get the physiotherapist's patients
        assigned_patients = AssignedPatient.objects.filter(physiotherapist_id=physiotherapist.id)
    else:
        assigned_patients = None

    return render(request, 'physiotherapist/home.html', {'assigned_patients': assigned_patients})


def toggle_patient_status(request):
    if request.method == 'GET':
        patient_id = request.GET.get('patient_id')
        try:
            assigned_patient = AssignedPatient.objects.get(id=patient_id)
            assigned_patient.is_active = not assigned_patient.is_active
            assigned_patient.save()
            return JsonResponse({'status': 'success', 'is_active': assigned_patient.is_active})
        except AssignedPatient.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Patient not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def patient_detail(request, patient_id):
    user_data = Report.objects.filter(user_id=patient_id).order_by('-date')
    return render(request, 'physiotherapist/patient_reoprt.html', {'user_data': user_data})