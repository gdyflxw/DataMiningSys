from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
#def index(request):
#    return HttpResponse("Hello, world. You're at the polls index.")

def index(request):
    uname=request.session.get('username',None)
    uright=request.session.get('right',0)
    userinfo={'uname':uname,'uright':uright}
    return render(request,'index.html',{'userinfo':userinfo})

def login(request):
    return render(request,'login.html')

def dashboard(request):
    return render(request,'dashboard.html')