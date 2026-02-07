"""
Authentication Views for UPG System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from .models import User, PasswordResetToken
from .forms import LoginForm, UserRegistrationForm


def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # Security fix: Validate next URL to prevent open redirect attacks
                next_url = request.GET.get('next', '/')
                if not url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure()
                ):
                    next_url = '/'
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view with village assignments for mentors and FAs"""
    user = request.user
    from accounts.models import UserProfile

    # Ensure user has a profile
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=user)

    # Role info for template
    role_info = {
        'is_mentor': user.role == 'mentor',
        'is_field_associate': user.role == 'field_associate',
        'is_program_manager': user.role == 'program_manager',
        'is_me_staff': user.role == 'me_staff',
        'is_ict_admin': user.role == 'ict_admin',
    }

    # Village info for mentors and field associates
    village_info = {
        'has_village_assignments': False,
        'assigned_villages_count': 0,
        'assigned_villages': [],
    }

    if user.role == 'mentor':
        # Mentors see their directly assigned villages
        if profile:
            villages = profile.assigned_villages.all().select_related('subcounty_obj')
            village_info['has_village_assignments'] = villages.exists()
            village_info['assigned_villages_count'] = villages.count()
            village_info['assigned_villages'] = villages

    elif user.role == 'field_associate':
        # FAs see villages from their supervised mentors
        from core.models import Village
        supervised_mentors = User.objects.filter(
            role='mentor',
            is_active=True,
            profile__supervisor=user
        ).select_related('profile')

        village_ids = []
        for mentor in supervised_mentors:
            if hasattr(mentor, 'profile') and mentor.profile:
                mentor_villages = list(mentor.profile.assigned_villages.values_list('id', flat=True))
                village_ids.extend(mentor_villages)
        village_ids = list(set(village_ids))

        if village_ids:
            villages = Village.objects.filter(id__in=village_ids).select_related('subcounty_obj')
            village_info['has_village_assignments'] = True
            village_info['assigned_villages_count'] = villages.count()
            village_info['assigned_villages'] = villages
            village_info['supervised_mentors_count'] = supervised_mentors.count()

    # Supervisor info for mentors
    supervisor_info = None
    if user.role == 'mentor' and profile and profile.supervisor:
        supervisor_info = {
            'name': profile.supervisor.get_full_name() or profile.supervisor.username,
            'email': profile.supervisor.email,
            'phone': profile.supervisor.phone_number if hasattr(profile.supervisor, 'phone_number') else '',
        }

    # Supervised mentors info for FAs
    supervised_mentors_info = []
    if user.role == 'field_associate':
        supervised_mentors = User.objects.filter(
            role='mentor',
            is_active=True,
            profile__supervisor=user
        ).select_related('profile')
        for mentor in supervised_mentors:
            mentor_villages = []
            if hasattr(mentor, 'profile') and mentor.profile:
                mentor_villages = list(mentor.profile.assigned_villages.values_list('name', flat=True))
            supervised_mentors_info.append({
                'name': mentor.get_full_name() or mentor.username,
                'email': mentor.email,
                'villages': mentor_villages,
            })

    context = {
        'user': user,
        'profile': profile,
        'role_info': role_info,
        'village_info': village_info,
        'supervisor_info': supervisor_info,
        'supervised_mentors_info': supervised_mentors_info,
    }

    return render(request, 'accounts/profile.html', context)


def forgot_password_view(request):
    """Forgot password form"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Deactivate any existing tokens for this user
            PasswordResetToken.objects.filter(user=user, is_active=True).update(is_active=False)

            # Create new reset token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', kwargs={'token': reset_token.token})
            )

            # Send email (you may want to use a template for this)
            subject = 'UPG System - Password Reset Request'
            message = f'''
Hello {user.get_full_name() or user.username},

You have requested to reset your password for the UPG Management System.

Please click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
UPG Management System
            '''

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                return redirect('accounts:password_reset_sent')
            except Exception as e:
                messages.error(request, 'Failed to send password reset email. Please contact system administrator.')

        except User.DoesNotExist:
            # Don't reveal whether email exists for security
            return redirect('accounts:password_reset_sent')

    return render(request, 'accounts/forgot_password.html')


def password_reset_sent_view(request):
    """Password reset email sent confirmation"""
    return render(request, 'accounts/password_reset_sent.html')


def reset_password_view(request, token):
    """Reset password with token"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            messages.error(request, 'This password reset link has expired or is invalid.')
            return redirect('accounts:forgot_password')

        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'accounts/reset_password.html', {'token': token})

            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'accounts/reset_password.html', {'token': token})

            # Reset password
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset_token.mark_as_used()

            messages.success(request, 'Your password has been reset successfully.')
            return redirect('accounts:password_reset_complete')

        return render(request, 'accounts/reset_password.html', {'token': token})

    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:forgot_password')


def password_reset_complete_view(request):
    """Password reset complete confirmation"""
    return render(request, 'accounts/password_reset_complete.html')