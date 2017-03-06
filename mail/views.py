from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Mail
from composeexample.OnlyOne import MySingleton
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp, SocialAccount

# Create your views here.
def home(request):
    try:
        SocialApp.objects.get_current("google")
    except SocialApp.DoesNotExist:
        app = SocialApp(provider='google', name='Google auth',
             client_id='553571003770-nidlauhlth4p8p97rtscoep5o728ttar.apps.googleusercontent.com',
             secret='BelhMtsI-l-GTV15fhtFW8uc')
        #
        app.save()
        app.sites.add(1) # or your site id

    context = {}
    template = "home.html"
    return render(request, template, context)


# Create your views here.
def profile(request):
    MySingleton.get_instance(request)

    mail_list = Mail.objects.all()
    paginator = Paginator(mail_list, 10)

    page = request.GET.get('page')
    try:
        mails = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mails = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mails = paginator.page(paginator.num_pages)


    #print(messages)
    context = {'mails': mails}
    template = "profile.html"
    return render(request, template, context)
