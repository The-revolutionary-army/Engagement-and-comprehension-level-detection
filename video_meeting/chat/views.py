from django.shortcuts import render

# Create your views here.
def main_view(request):
    return render(request, 'chat/index.html', context={})

