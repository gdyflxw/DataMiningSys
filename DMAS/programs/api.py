from django.http import HttpResponse
from . import dbtools
import json
from ..models import webusers


def apis(requests):    
    methodname=requests.POST.get('methodname')
    parameters=json.loads(requests.POST.get('parameters'))
    if methodname=='login':
        result=login_check(parameters)
        userinfo=result['userinfo']
        requests.session['username']=userinfo['username']
        requests.session['right']=userinfo['right']
        rs=result['rs']
        return HttpResponse(json.dumps(rs,ensure_ascii=False),content_type="application/json")
    if methodname=='logout':
        requests.session['username']=None
        requests.session['right']=0
        rs={"info":"<strong>您已成功退出！</strong>"}
        return HttpResponse(json.dumps(rs,ensure_ascii=False),content_type="application/json")

def login_check(p):
    uname=p['username']
    upwd=p['passwd']
    try:
        if webusers.objects.get(username=uname).pwd==upwd:
            rs={"rs":{"accessGranted":True},"userinfo":{"username":uname,"right":webusers.objects.get(username=uname).right}}
        else:
            rs={"rs":{"accessGranted":False,"errors":"<strong>登录失败！</strong><br />请输入正确的用户名/密码"},"userinfo":{"username":None,"right":0}}
    except:
        rs={"rs":{"accessGranted":False,"errors":"<strong>登录失败！</strong><br />用户名不存在！"},"userinfo":{"username":None,"right":0}}
    return rs