from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render
from django.http import HttpResponse
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


def password_reset_form(request):
    subject = request.POST.get("subject", "")
    message = request.POST.get("message", "")
    from_email = request.POST.get("from_email", "")
    try:
        send_mail(
            subject,
            message,
            from_email,
            ["admin@example.com"]
        )
    except BadHeaderError:
        return HttpResponse("Invalid header found.")
    return render(request, "users/password_reset_form.html")
