from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
import json


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

def stockInfo(request):
    return render(request,'stockInfo.html')

def incInfo(request):
    return render(request,'incInfo.html')

def cancelInfo(request):
    return render(request,'cancelInfo.html')

def industryInfo(request):
    return render(request,'industryInfo.html')

def stathy(request):
    return render(request,'stathy.html')

def moveInfo(request):
    return render(request,'moveInfo.html')

def capitalInfo(request):
    return render(request,'capitalInfo.html')

def invFrom(request):
    return render(request,'invFrom.html')

def starEnt(request):
    return render(request,'starEnt.html')

def sifu(request):
    return render(request,'sifu.html')
    
def mapDetail(request):
    return render(request,'mapDetail.html')



def tmpjs(reuqest):
    rs=json.load(open("E:/tmpjs.json",encoding='utf-8'))
    return HttpResponse(json.dumps(rs,ensure_ascii=False),content_type="application/json")

def download(request,filename):
    print(filename)
    filepath='F:/ShareFiles/'
    file=open(filepath+filename,'rb')  
    response =FileResponse(file)  
    response['Content-Type']='application/octet-stream'  
    response['Content-Disposition']='attachment;filename="%s"'%filename
    return response