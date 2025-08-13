from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from SCP_PORTAL.models import UserProfile  # adjust if your model is elsewhere
from django.contrib.auth import authenticate, login as auth_login ,logout # ✅ alias to avoid conflict
from SCP_PORTAL.models import StudentProfile
from django.contrib.auth.decorators import login_required , user_passes_test

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F, Window, IntegerField, ExpressionWrapper
from django.db.models.functions import RowNumber, Coalesce

# Adding some import for offer letter generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse
from django.utils import timezone

from Student.settings import BASE_DIR  # adjust if needed







 

# This function renders the HOMEPAGE
def index(request):
    return render(request, 'index.html')



# This function handles user signup


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        role     = request.POST.get('role')  # 'student' or 'admin'

        # Prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')

        # Create the base User
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create their UserProfile with the selected role
        UserProfile.objects.create(user=user, role=role)

        # ✅ Do NOT create StudentProfile here — wait until they submit personal info

        messages.success(request, f'{role.capitalize()} account created successfully!')
        return redirect('login_view')

    return render(request, 'signup.html')



# This function handles user login
def login_view(request):
   
    return render(request, 'login_view.html')



# Admin Login View
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        print("DEBUG: admin_login reached")
        print("DEBUG: user =", user)

        if not user:
            messages.error(request, 'Invalid credentials.')
            return redirect('login_view')

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('login_view')

        print("DEBUG: role =", profile.role)
        print("DEBUG: is_staff_admin =", profile.is_staff_admin)

        if profile.role == 'admin' and profile.is_staff_admin:
            auth_login(request, user)
            # This is for logging 
            next_url = request.GET.get('next') or request.POST.get('next')
           # print("DEBUG: Redirecting to staff_admin_panel")
            return redirect(next_url or 'staff_admin_panel')  # ✅ Redirect, don't render here


        else:
            messages.error(request, 'Access denied. Not a staff admin.')
            return redirect('login_view')

    return render(request, 'login_view.html')


# Student Login View

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role.lower() == 'student':
                    auth_login(request, user)
                    return redirect('student_dashboard')
                else:
                    messages.error(request, 'Access denied. Not a student account.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
        else:
            messages.error(request, 'Invalid credentials.')

        return redirect('login_view')  # Redirect back to student login modal

    # Optional: render a fallback page if someone visits this URL directly
    return render(request, 'student_login_fallback.html')


# Student Dashboard View
def is_student(user):
    try:
        return user.userprofile.role.lower() == 'student'
    except UserProfile.DoesNotExist:
        return False
# Student Dashboard

@login_required
def student_dashboard(request):
    # ✅ Only allow student accounts in
    if not is_student(request.user):
        messages.error(request, "Only students can access the student dashboard.")
        return redirect('/')

    # ✅ Try to get this student's record (can be None if they haven't filled info yet)
    student = StudentProfile.objects.filter(user=request.user).first()

    # Default flags if no profile yet
    submitted = allocated = accepted = payment_verified = False
    status = "Please fill in your personal details to begin"
    can_accept = can_upload_receipt = False

    if student:
        submitted = bool(student.full_name and student.age and student.gender and student.contact)
        allocated = bool(student.allocated_branch)
        accepted = getattr(student, 'branch_accepted', False)
        payment_verified = getattr(student, 'payment_verified', False)

        # ✅ Human‑friendly status
        if not allocated:
            status = "Waiting for allocation"
            can_accept = False
            can_upload_receipt = False
        elif allocated and not accepted:
            status = f"Allocated: {student.allocated_branch}"
            can_accept = True
            can_upload_receipt = False
        elif accepted and not payment_verified:
            status = f"Accepted: {student.allocated_branch} — Payment pending"
            can_accept = False
            can_upload_receipt = True
        else:
            status = f"Offer confirmed: {student.allocated_branch}"
            can_accept = False
            can_upload_receipt = False

    context = {
        'student': student,
        'submitted': submitted,
        'allocated': allocated,
        'accepted': accepted,
        'payment_verified': payment_verified,
        'status': status,
        'can_accept': can_accept,
        'can_upload_receipt': can_upload_receipt,
    }
    return render(request, 'student_dashboard.html', context)


@login_required
def accept_allocation(request):
    # Ensure only students can run this
    if not is_student(request.user):
        messages.error(request, "Only students can accept allocations.")
        return redirect('home')

    student = get_object_or_404(StudentProfile, user=request.user)

    if not student.allocated_branch:
        messages.error(request, "No branch allocated yet.")
        return redirect('student_dashboard')

    # Mark as accepted
    student.branch_accepted = True
    student.save()

    messages.success(request, f"You have accepted your allocated branch: {student.allocated_branch}")
    return redirect('student_dashboard')


@login_required
def upload_receipt(request):
    if not is_student(request.user):
        messages.error(request, "Only students can upload receipts.")
        return redirect('home')

    student = get_object_or_404(StudentProfile, user=request.user)

    if request.method == 'POST':
        uploaded_file = request.FILES.get('receipt')
        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('upload_receipt')

        student.receipt = uploaded_file
        student.save()

        messages.success(request, "Receipt uploaded successfully!")
        return redirect('student_dashboard')

    return render(request, 'upload_receipt.html', {'student': student})



@login_required
def submit_personal_info(request):
    if request.method == 'POST':
        # 1) Grab form values
        full_name = request.POST.get('full_name')
        age       = request.POST.get('age')
        gender    = request.POST.get('gender')
        contact   = request.POST.get('contact')

        # 2) Create or update in one go
        #    This will only INSERT when all non-null fields are provided.
        StudentProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'full_name': full_name,
                'age':       age,
                'gender':    gender,
                'contact':   contact,
            }
        )

        messages.success(
            request,
            'Personal information saved successfully! Proceed to education details.'
        )
        return redirect('education_info')

    return redirect('student_dashboard')


@login_required
def education_info(request):
    """
    Step 2 (GET): Render the education-details form,
    passing the existing profile for prefilling.
    """
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, 'education_info.html', {
        'profile': profile
    })

@login_required
def submit_education_info(request):
    if request.method != 'POST':
        return redirect('education_info')

    def parse_int(key):
        raw = request.POST.get(key, '').strip()
        try:
            return int(raw)
        except (ValueError, TypeError):
            return None

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    # 10th Grade
    profile.school_10   = request.POST.get('school_10', '')
    profile.tenth_board = request.POST.get('tenth_board', '')
    profile.year_10     = parse_int('year_10')
    profile.maths_10    = parse_int('maths_10')
    profile.science_10  = parse_int('science_10')
    profile.english_10  = parse_int('english_10')
    profile.social_10   = parse_int('social_10')

    # 12th Grade
    profile.school_12      = request.POST.get('school_12', '')
    profile.twelfth_board  = request.POST.get('twelfth_board', '')
    profile.twelfth_stream = request.POST.get('twelfth_stream', '')
    profile.year_12        = parse_int('year_12')
    profile.physics_12     = parse_int('physics_12')
    profile.chemistry_12   = parse_int('chemistry_12')
    profile.maths_12       = parse_int('maths_12')
    profile.english_12     = parse_int('english_12')

    profile.calculate_percentages()
    profile.save()

    messages.success(request, 'Educational information saved successfully!')
    return redirect('choice_filling')


@login_required
def choice_filling(request):
    """
    Step 3 (GET): Render the choice-filling form.
    """
    # ensure profile exists
    StudentProfile.objects.get_or_create(user=request.user)
    return render(request, 'choice_filling.html')


@login_required
def submit_choices(request):
    """
    Step 3 (POST): Save the three choices and return to dashboard.
    """
    if request.method == 'POST':
        profile = get_object_or_404(StudentProfile, user=request.user)
        profile.choice_1 = request.POST.get('choice_1')
        profile.choice_2 = request.POST.get('choice_2')
        profile.choice_3 = request.POST.get('choice_3')
        profile.save()

        messages.success(request, 'Your choices have been submitted successfully!')
        return redirect('student_dashboard')

    return redirect('choice_filling')



# LOGIC OF OVERALL ADMIN PANEL AND SEAT ALLOCATION
def is_staff_admin(user):
    try:
        return user.userprofile.role == 'admin' and user.userprofile.is_staff_admin
    except UserProfile.DoesNotExist:
        return False
@login_required
def staff_admin_panel(request):
    print("DEBUG user:", request.user, "is_authenticated:", request.user.is_authenticated)
    print("DEBUG is_staff_admin:", is_staff_admin(request.user))
    if not is_staff_admin(request.user):
        return render(request, 'unauthorized.html', status=403)

    # Handle manual allocation from the panel (optional inline form post)
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        allocated_branch = request.POST.get('allocated_branch', '').strip()
        if student_id and allocated_branch:
            student = get_object_or_404(StudentProfile, id=student_id)
            student.allocated_branch = allocated_branch
            student.save()
            messages.success(request, f"Allocated {allocated_branch} to {student.full_name}.")
        return redirect('staff_admin_panel')

    # Safe sums with Coalesce to avoid None arithmetic
    tenth_total = (
        Coalesce(F('maths_10'), 0) + Coalesce(F('science_10'), 0) +
        Coalesce(F('english_10'), 0) + Coalesce(F('social_10'), 0)
    )
    twelfth_total = (
        Coalesce(F('physics_12'), 0) + Coalesce(F('chemistry_12'), 0) +
        Coalesce(F('maths_12'), 0) + Coalesce(F('english_12'), 0)
    )

    students = (
        StudentProfile.objects
        .annotate(
            tenth_total=ExpressionWrapper(tenth_total, output_field=IntegerField()),
            twelfth_total=ExpressionWrapper(twelfth_total, output_field=IntegerField()),
        )
        .annotate(
            total_marks=ExpressionWrapper(
                F('tenth_total') + F('twelfth_total'),
                output_field=IntegerField()
            )
        )
        .annotate(
            rank=Window(
                expression=RowNumber(),
                order_by=[F('total_marks').desc(), F('twelfth_total').desc()]
            )
        )
        .order_by('-total_marks', '-twelfth_total')
    )

    return render(request, 'staff_admin_panel.html', {'students': students})


@login_required
def allocate_branch(request, student_id):
    if not is_staff_admin(request.user):
        return render(request, 'unauthorized.html')

    student = get_object_or_404(StudentProfile, id=student_id)
    # assign first non-empty choice
    for choice in (student.choice_1, student.choice_2, student.choice_3):
        if choice:
            student.allocated_branch = choice
            break
    student.save()
    return redirect('admin_panel')




@login_required
def toggle_acceptance(request, student_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role != 'admin' or not profile.is_staff_admin:
        return render(request, 'unauthorized.html')

    student = get_object_or_404(StudentProfile, id=student_id)
    student.branch_accepted = not student.branch_accepted
    student.save()
    messages.success(request, f"Acceptance status updated for {student.full_name}.")
    return redirect('staff_admin_panel')

@login_required
def verify_payment(request, student_id):
    if not is_staff_admin(request.user):
        return render(request, 'unauthorized.html', status=403)

    student = get_object_or_404(StudentProfile, id=student_id)

    # Toggle payment_verified
    student.payment_verified = not student.payment_verified
    student.save()

    status = "verified" if student.payment_verified else "unverified"
    messages.success(request, f"Payment marked as {status} for {student.full_name}.")
    return redirect('staff_admin_panel')

def logout_view(request):
    logout(request)  # Clears the session
    return redirect('/')  # 'home' is the name of your homepage URL pattern



# Offer Letter Generation 

@login_required
def generate_offer_letter(request, student_id):
    if not is_staff_admin(request.user):
        return render(request, 'unauthorized.html', status=403)

    student = get_object_or_404(StudentProfile, id=student_id)

    if not student.branch_accepted or not student.payment_verified:
        messages.error(request, "Offer letter can only be generated after acceptance and payment verification.")
        return redirect('staff_admin_panel')

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Offer_Letter_{student.full_name}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 🏫 Institute Logo (optional)
    logo_path = BASE_DIR / 'static' / 'images' / 'institute_logo.png'  # adjust path
    try:
        logo = ImageReader(str(logo_path))
        p.drawImage(logo, x=40, y=height - 160, width=80, preserveAspectRatio=True, mask='auto')
    except:
        pass  # skip if logo not found

    # 🏫 Institute Name
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 120, "Birla Institute of Applied Sciences")
    p.setLineWidth(0.5)
    p.line(50, height - 140, width - 50, height - 140)

    # 📅 Date and student info
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 160, f"Date of Issue: {timezone.now().strftime('%d %B %Y')}")
    p.drawString(100, height - 190, f"Student Name: {student.full_name}")
    p.drawString(100, height - 210, f"Allocated Branch: {student.allocated_branch}")

    # 🎓 Confirmation message
    p.drawString(100, height - 350, "Dear Candidate,")
    p.drawString(100, height - 370, "We are pleased to inform you that your seat has been successfully allocated.")
    p.drawString(100, height - 390, "Please report to campus with this letter and your original documents.")
    p.drawString(100, height - 310, "We look forward to welcoming you to our institute.")

    # Signature block
    p.setFont("Helvetica-Bold", 12)
    p.drawString(430, height - 590, "Authorized Signature")



    # 🖋 Signature block
    p.setFont("Helvetica", 12)
 
    p.drawString(100, height - 580, "Sincerely,")
    p.drawString(100, height - 600, "Admissions Office")
    p.drawString(100, height - 620, "Birla Institute of Applied Sciences")

    # 🖼 Signature image (optional)
    signature_path = BASE_DIR / 'static' / 'images' / 'signature.png'
    try:
        signature = ImageReader(str(signature_path))
        p.drawImage(signature, x=420, y=height - 780, width=120, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # 📍 Footer
    p.setLineWidth(0.3)
    p.line(50, 100, width - 50, 100)
    p.setFont("Helvetica-Oblique", 11)
    p.drawString(100, 80, "Birla Institute of Applied Sciences, Bhimtal, Uttarakhand – 263136")
    p.drawString(100, 65, "Phone: +91-5942-220444 | Email: info@bias.ac.in")
    p.drawString(100, 50, "This is a system-generated document and does not require a physical signature.")

    p.showPage()
    p.save()

    return response


# Download Offer Letter for Students
@login_required
def download_offer_letter(request):
    if not is_student(request.user):
        return render(request, 'unauthorized.html', status=403)

    student = get_object_or_404(StudentProfile, user=request.user)

    if not student.branch_accepted or not student.payment_verified:
        messages.error(request, "Offer letter is only available after acceptance and payment verification.")
        return redirect('student_dashboard')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Offer_Letter_{student.full_name}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 🏫 Institute Logo (optional)
    logo_path = BASE_DIR / 'static' / 'images' / 'institute_logo.png'  # adjust path
    try:
        logo = ImageReader(str(logo_path))
        p.drawImage(logo, x=40, y=height - 160, width=80, preserveAspectRatio=True, mask='auto')
    except:
        pass  # skip if logo not found

    # 🏫 Institute Name
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 120, "Birla Institute of Applied Sciences")
    p.setLineWidth(0.5)
    p.line(50, height - 140, width - 50, height - 140)

    # 📅 Date and student info
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 160, f"Date of Issue: {timezone.now().strftime('%d %B %Y')}")
    p.drawString(100, height - 190, f"Student Name: {student.full_name}")
    p.drawString(100, height - 210, f"Allocated Branch: {student.allocated_branch}")

    # 🎓 Confirmation message
    p.drawString(100, height - 350, "Dear Candidate,")
    p.drawString(100, height - 370, "We are pleased to inform you that your seat has been successfully allocated.")
    p.drawString(100, height - 390, "Please report to campus with this letter and your original documents.")
    p.drawString(100, height - 310, "We look forward to welcoming you to our institute.")

    # Signature block
    p.setFont("Helvetica-Bold", 12)
    p.drawString(430, height - 590, "Authorized Signature")



    # 🖋 Signature block
    p.setFont("Helvetica", 12)
 
    p.drawString(100, height - 580, "Sincerely,")
    p.drawString(100, height - 600, "Admissions Office")
    p.drawString(100, height - 620, "Birla Institute of Applied Sciences")

    # 🖼 Signature image (optional)
    signature_path = BASE_DIR / 'static' / 'images' / 'signature.png'
    try:
        signature = ImageReader(str(signature_path))
        p.drawImage(signature, x=420, y=height - 780, width=120, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # 📍 Footer
    p.setLineWidth(0.3)
    p.line(50, 100, width - 50, 100)
    p.setFont("Helvetica-Oblique", 11)
    p.drawString(100, 80, "Birla Institute of Applied Sciences, Bhimtal, Uttarakhand – 263136")
    p.drawString(100, 65, "Phone: +91-5942-220444 | Email: info@bias.ac.in")
    p.drawString(100, 50, "This is a system-generated document and does not require a physical signature.")

    p.showPage()
    p.save()

    return response

