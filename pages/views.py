from django.shortcuts import render

def faq(request):
    return render(request, 'pages/placeholder.html', {'title': 'FAQ'})
#    return render(request, 'pages/faq.html')

def contact(request):
    return render(request, 'pages/placeholder.html', {'title': 'Contact WattTime'})
#    return render(request, 'pages/contact.html')

def about_us(request):
    return render(request, 'pages/placeholder.html', {'title': 'About WattTime'})
#    return render(request, 'pages/about_us.html')

def how_it_works(request):
    return render(request, 'pages/placeholder.html', {'title': 'How WattTime works'})
#    return render(request, 'pages/how_it_works.html')

