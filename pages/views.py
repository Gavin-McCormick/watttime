from django.shortcuts import render
#from django.contrib.auth.decorators import login_required

def faq(request):
    return render(request, 'pages/faq.html')

def contact(request):
    return render(request, 'pages/contact.html')


