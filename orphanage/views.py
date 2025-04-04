from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import User, Child, Caretaker, Donation, AdoptionRequest,Report,Feedback,TimeTable, DietPlan,AdoptedChild
from django.contrib import messages
from django.db.models import Q
from datetime import date,datetime
from django.db.models import Sum
import os
from django.conf import settings
from django.http import JsonResponse
import json
from django.shortcuts import redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.contrib.auth.models import User  # Import your custom User model
from datetime import datetime, date
from django.shortcuts import render
from django.contrib import messages
from .models import Caretaker  # Import the Caretaker model
from datetime import datetime, date
from django.contrib import messages
from .models import Caretaker, User  # Import your custom User model

from django.conf import settings
from django.db.models import Sum
from .models import Donation, Child, Caretaker, Feedback, Details


# -------------------- USER AUTHENTICATION --------------------




def home(request):
    # Fetch total donations, children, and caretakers from the database
    total_donations = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_children = Child.objects.count()
    total_caretakers = Caretaker.objects.count()
    children = Child.objects.all()
    feedbacks = Feedback.objects.order_by('-created_at')[:5]

    # Fetch images from the "media/hero_images/" folder
    hero_images_folder = os.path.join(settings.MEDIA_ROOT, 'hero_images')
    hero_images = []

    if os.path.exists(hero_images_folder):
        for file in os.listdir(hero_images_folder):
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                hero_images.append(f"{settings.MEDIA_URL}hero_images/{file}")

    # Fetch latest details record
    details = Details.objects.last()  # Get the most recent entry

    context = {
        'feedbacks': feedbacks,
        'total_donations': total_donations,
        'total_children': total_children,
        'total_caretakers': total_caretakers,
        'children': children,
        'hero_images': hero_images,  # Passing the hero images list
        'details': details,  # Pass details to the template
    }
    return render(request, 'home.html', context)



@login_required
def admin_dashboard(request):
    feedbacks = Feedback.objects.order_by('-created_at')
    total_donations = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_children = Child.objects.count()
    total_caretakers = Caretaker.objects.count()
    children = Child.objects.all()
    donations = Donation.objects.select_related('user').order_by('-date')  # Fetch all donation details

    return render(request, 'admin_dashboard.html', {
        'total_donations': total_donations,
        'total_children': total_children,
        'total_caretakers': total_caretakers,
        'feedbacks': feedbacks,
        'donations': donations,  # Pass donation details to template
    })

# Login View (Handles Admin, Caretaker, and User)
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# -------------------- USER REGISTRATION --------------------

def register_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        dob_str = request.POST['dob']
        place = request.POST['place']
        aadhaar_number = request.POST['aadhaar_number']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register_user')

        # ✅ Convert `dob_str` to a `date` object
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid Date of Birth format. Use YYYY-MM-DD.")
            return redirect('register_user')

        # ✅ Django will calculate `age` automatically in `save()` method
        user = User.objects.create_user(
            username=username, 
            password=password, 
            first_name=first_name, 
            last_name=last_name, 
            dob=dob, 
            place=place, 
            aadhaar_number=aadhaar_number
        )
        user.save()

        messages.success(request, "User registered successfully!")
        return redirect('login')

    return render(request, 'register_user.html')

def register_caretaker(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob_str = request.POST['dob']
        phone_number = request.POST['phone_number']
        experience = request.POST['experience']
        aadhaar_number = request.POST['aadhaar_number']
        place = request.POST['place']
        education = request.POST['education']
        marital_status = request.POST['marital_status']
        id_proof = request.FILES['id_proof']
        experience_certificate = request.FILES['experience_certificate']
        password = request.POST['phone_number']

        # Convert DOB string to a date object
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return redirect('register_caretaker')

        # Calculate age
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Create User instance using the custom model
        user = User.objects.create(
            username=name,  # Unique identifier
            dob=dob,
            age=age,
            place=place,
            aadhaar_number=aadhaar_number
        )
        user.set_password(password)  # Hash the password
        user.save()

        # Create Caretaker object and link to User
        caretaker = Caretaker.objects.create(
            user=user,  # Link to the User model
            name=name,
            dob=dob,
            age=age,
            phone_number=phone_number,
            experience=experience,
            aadhaar_number=aadhaar_number,
            place=place,
            education=education,
            marital_status=marital_status,
            id_proof=id_proof,
            experience_certificate=experience_certificate,
            status='Not Approved'
        )
        caretaker.save()

        messages.success(request, "Caretaker registration submitted for approval.")
        return redirect('admin_dashboard')

    return render(request, 'register_caretaker.html')

# Register New Child
@login_required
def register_child(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob_str = request.POST['dob']  # Get DOB as a string
        health_status = request.POST['health_status']
        photo = request.FILES['photo']
        additional_photos = request.FILES.getlist('additional_photos')
        caretaker_id = request.POST.get('caretaker')  # Get selected caretaker ID

        # Convert DOB string to a date object
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()  # Convert to date object
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return redirect('register_child')

        # Calculate age correctly
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Convert additional photo names to a list
        photo_urls = [photo.name for photo in additional_photos]

        # Fetch the caretaker object
        caretaker = None
        if caretaker_id:
            try:
                caretaker = Caretaker.objects.get(id=caretaker_id)
            except Caretaker.DoesNotExist:
                messages.error(request, "Invalid caretaker selected.")
                return redirect('register_child')

        # Create Child object
        child = Child.objects.create(
            name=name, dob=dob, age=age, health_status=health_status,
            photo=photo, additional_photos=photo_urls, status='Not Adopted',
            caretaker=caretaker  # Assign caretaker to the child
        )
        child.save()
        messages.success(request, "Child registered successfully.")
        return redirect('admin_dashboard')

    # Fetch all available caretakers for selection
    caretakers = Caretaker.objects.all()
    return render(request, 'register_child.html', {'caretakers': caretakers})

# -------------------- DONATIONS --------------------

# Make a Donation
@login_required
def donate(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        message = request.POST.get('message', '')

        donation = Donation.objects.create(user=request.user, amount=amount, message=message)
        donation.save()
        messages.success(request, "Thank you for your donation!")
        return redirect('home')

    return render(request, 'donate.html')

# -------------------- ADOPTION REQUEST --------------------

@login_required
def adoption_request(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob_str = request.POST['dob']
        family_members = request.POST['family_members']
        reason = request.POST['reason']
        annual_income = request.POST['annual_income']
        job_name = request.POST['job_name']
        company = request.POST['company']
        aadhaar_number = request.POST['aadhaar_number']
        phone_number = request.POST['phone_number']
        email_id = request.POST['email_id']
        id_proof = request.FILES['id_proof']
        income_certificate = request.FILES['income_certificate']
        salary_certificate = request.FILES.get('salary_certificate', None)

        # Convert DOB string to date
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return redirect('adoption_request')

        # Calculate age
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Retrieve child details from request
        child_id = request.GET.get('child_id', None)
        child_name = request.GET.get('child_name', '')
        child_age = request.GET.get('child_age', None)

        # Ensure child_id is provided
        if not child_id:
            messages.error(request, "Child information is missing.")
            return redirect('home')

        # Create AdoptionRequest object
        adoption = AdoptionRequest.objects.create(
            name=name, dob=dob, age=age, family_members=family_members,
            reason=reason, annual_income=annual_income, job_name=job_name,
            company=company, aadhaar_number=aadhaar_number, phone_number=phone_number,
            email_id=email_id, id_proof=id_proof, income_certificate=income_certificate,
            salary_certificate=salary_certificate, status='Pending',
            child_id=child_id, child_name=child_name, child_age=child_age
        )
        adoption.save()
        messages.success(request, "Adoption request submitted successfully.")
        return redirect('home')

    # Get child details from URL parameters
    child_id = request.GET.get('child_id', '')
    child_name = request.GET.get('child_name', '')
    child_age = request.GET.get('child_age', '')

    return render(request, 'adoption_request.html', {
        'child_id': child_id,
        'child_name': child_name,
        'child_age': child_age
    })

# -------------------- ADMIN DASHBOARD VIEWS --------------------

# Fetch All Adoption Requests (For Admin)
@login_required
def fetch_adoption_requests(request):
    if not request.user.is_superuser:
        return redirect('unauthorized')  # Redirect to an unauthorized page

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        new_status = request.POST.get("status")
        
        try:
            adoption_request = AdoptionRequest.objects.get(id=request_id)
            adoption_request.status = new_status
            adoption_request.save()
        except AdoptionRequest.DoesNotExist:
            return redirect('adoption_requests_list')

    adoption_requests = AdoptionRequest.objects.all()
    return render(request, 'adoption_requests_list.html', {'adoption_requests': adoption_requests})

# Fetch All Caretakers (For Admin)
@login_required
def fetch_caretakers(request):
    if not request.user.is_superuser:
        return redirect('unauthorized')  # Redirect to an unauthorized page
    
    caretakers = Caretaker.objects.all()
    return render(request, 'caretakers_list.html', {'caretakers': caretakers})

@login_required
def fetch_children(request):

    children = Child.objects.all()
    return render(request, 'children_list.html', {'children': children})

@login_required
def fetch_admin_children(request):

    children = Child.objects.all()
    return render(request, 'admin_child_list.html', {'children': children})


@login_required
def fetch_reports(request):
    if not request.user.is_superuser:
        return redirect('unauthorized')  # Redirect to an unauthorized page
    
    reports = Report.objects.all()  # Fetch reports with caretakers
    return render(request, 'reports_list.html', {'reports': reports})


def delete_caretaker(request, caretaker_id):
    caretaker = get_object_or_404(Caretaker, id=caretaker_id)
    caretaker.delete()
    messages.success(request, "Caretaker deleted successfully.")
    return redirect('fetch_caretakers') 

def submit_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            message = data.get('message')

            if not name or not message:
                return JsonResponse({'success': False, 'error': 'Missing fields'})

            Feedback.objects.create(name=name, message=message)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'feedback.html')



from django.utils.dateparse import parse_date

def caretaker_login(request):
    if request.method == "POST":
        name = request.POST.get("name")
        dob = request.POST.get("dob")

        try:
            user = User.objects.get(username=name, dob=dob)
            caretaker = Caretaker.objects.get(user=user)

            if caretaker.status == "Not Approved":
                login(request, user)
                return redirect("caretaker_dashboard")
            else:
                return render(request, "caretaker_login.html", {"error": "Caretaker not approved."})
        except (User.DoesNotExist, Caretaker.DoesNotExist):
            return render(request, "caretaker_login.html", {"error": "Invalid Name or Date of Birth."})

    return render(request, "caretaker_login.html")


@login_required
def caretaker_dashboard(request):
    caretaker = get_object_or_404(Caretaker, user=request.user)

    assigned_children = Child.objects.filter(caretaker=caretaker)
    total_children = assigned_children.count()
    
    # Fetch schedules and diet plans
    timetables = TimeTable.objects.filter(caretaker=caretaker)
    diet_plans = DietPlan.objects.filter(caretaker=caretaker)

    return render(request, 'caretaker_dashboard.html', {
        'caretaker': caretaker,
        'total_children': total_children,
        'assigned_children': assigned_children,
        'timetables': timetables,
        'diet_plans': diet_plans,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Child, TimeTable, DietPlan, Report

@login_required
def edit_child_details(request, child_id):
    child = get_object_or_404(Child, id=child_id, caretaker=request.user)

    if request.method == 'POST':
        child.name = request.POST['name']
        child.dob = request.POST['dob']
        child.health_status = request.POST['health_status']
        child.status = request.POST['status']

        if 'photo' in request.FILES:
            if child.photo:
                default_storage.delete(child.photo.path)  # Delete old photo
            child.photo = request.FILES['photo']

        if 'additional_photos' in request.FILES:
            additional_photos = request.FILES.getlist('additional_photos')
            for photo in additional_photos:
                child.additional_photos.append(str(photo))

        child.save()
        return JsonResponse({'message': 'Child details updated successfully'})

    return JsonResponse({
        'name': child.name,
        'dob': child.dob,
        'health_status': child.health_status,
        'status': child.status,
        'photo_url': child.photo.url if child.photo else '',
        'additional_photos': child.additional_photos,
    })


@login_required
def add_or_edit_timetable(request, child_id):
    child = get_object_or_404(Child, id=child_id, caretaker=request.user)

    if request.method == 'POST':
        date = request.POST['date']
        activity = request.POST['activity']

        timetable, created = TimeTable.objects.update_or_create(
            child=child, date=date, defaults={'activity': activity}
        )
        return JsonResponse({'message': 'Timetable updated successfully'})

    timetables = TimeTable.objects.filter(child=child).values()
    return JsonResponse({'timetables': list(timetables)})


@login_required
def add_or_edit_dietplan(request, child_id):
    child = get_object_or_404(Child, id=child_id, caretaker=request.user)

    if request.method == 'POST':
        date = request.POST['date']
        meal = request.POST['meal']
        description = request.POST['description']

        diet_plan, created = DietPlan.objects.update_or_create(
            child=child, date=date, defaults={'meal': meal, 'description': description}
        )
        return JsonResponse({'message': 'Diet plan updated successfully'})

    diet_plans = DietPlan.objects.filter(child=child).values()
    return JsonResponse({'diet_plans': list(diet_plans)})


@login_required
def add_report(request):
    if request.method == 'POST':
        child_id = request.POST.get('child_id')
        title = request.POST.get('title')
        content = request.POST.get('content')

        print(f"Received child_id: {child_id}, title: {title}, content: {content}")

        if child_id and title and content:
            child = get_object_or_404(Child, id=child_id)
            print(f"Found child: {child.name}")

            caretaker = Caretaker.objects.filter(user=request.user).first()
            print(f"Found caretaker: {caretaker}")

            if not caretaker:
                print("Caretaker not found. Redirecting to caretaker_dashboard.")
                return redirect('caretaker_dashboard')

            try:
                Report.objects.create(
                    child_name=child.name,
                    caretaker_name=caretaker.name,
                    title=title,
                    content=content
                )
                print("Report successfully created.")
                return redirect('caretaker_dashboard')
            except Exception as e:
                print(f"Error while creating report: {e}")
                return redirect('caretaker_dashboard')

    print("Redirecting to login due to missing POST data.")
    return redirect('login')




from datetime import datetime

@login_required
def edit_child(request, child_id):
    child = get_object_or_404(Child, id=child_id)

    if request.method == 'POST':
        child.name = request.POST.get('name')
        child.age = request.POST.get('age')
        child.gender = request.POST.get('gender')

        dob_str = request.POST.get('dob')
        if dob_str:
            try:
                child.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()  # Convert string to date
            except ValueError:
                # Handle invalid date format
                messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
                return redirect('caretaker_dashboard')

        if 'photo' in request.FILES:
            child.photo = request.FILES['photo']

        child.save()
        return redirect('caretaker_dashboard')

    return redirect('caretaker_dashboard')




def delete_child(request, child_id):
    child = get_object_or_404(Child, id=child_id)

    if request.method == "POST":
        # Store child details before deletion
        AdoptedChild.objects.create(
            name=child.name,
            age=child.age,
            health_status=child.health_status
        )

        # Delete the child record
        child.delete()
        messages.success(request, "Child record moved to adopted children.")

        return redirect('fetch_admin_children')  # Update with your actual view

    return redirect('fetch_admin_children')


def adopted_children_list(request):
    adopted_children = AdoptedChild.objects.all()
    return render(request, 'adopted_child.html', {'adopted_children': adopted_children})
