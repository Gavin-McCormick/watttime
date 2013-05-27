from django.shortcuts import render

def faq(request):
    return render(request, 'pages/placeholder.html', {'title': 'FAQ'})

def contact(request):
    return render(request, 'pages/placeholder.html', {'title': 'Contact WattTime'})

def about_us(request):
    return render(request, 'pages/placeholder.html', {'title': 'About WattTime'})

def how_it_works(request):
    return render(request, 'pages/placeholder.html', {'title': 'How WattTime works'})

