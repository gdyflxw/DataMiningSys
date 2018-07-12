from django.http import HttpResponse
from . import dbtools
import json
from ..models import webusers
from DMAS.programs.getData import *

def apis(requests):    
    methodname=requests.POST.get('methodname')
    parameters=json.loads(requests.POST.get('parameters'))
    rs=None
    #登录
    if methodname=='login':
        result=login_check(parameters)
        userinfo=result['userinfo']
        requests.session['username']=userinfo['username']
        requests.session['right']=userinfo['right']
        rs=result['rs']
        
    #登出
    if methodname=='logout':
        requests.session['username']=None
        requests.session['right']=0
        rs={"info":"<strong>您已成功退出！</strong>"}

    #按行政区划统计各月信息
    if methodname=='xzqhpmon':
        rs=xzqhpmon(parameters)

    #按截止日期统计行政区划的信息
    if methodname=='monpxzqh':
        rs=monpxzqh(parameters)

    #按行政区划统计行政区划的日增量
    if methodname=='dailyinc':
        rs=dailyinc(parameters)

    #按截止日期统计16年1月到现在的月增量
    if methodname=='monthlyinc':
        rs=monthlyinc(parameters)

    #按行业统计注销的本期、同比、环比信息
    if methodname=='cancelhy':
        rs=cancelhy(parameters)

    if methodname=='cancelqh':
        rs=cancelqh(parameters)

    if methodname=='canceldt':
        rs=canceldt(parameters)

    if methodname=='SrvIndhy':
        rs=SrvIndhy(parameters)

    if methodname=='SrvIndqh':
        rs=SrvIndqh(parameters)

    if methodname=='StatCY':
        rs=StatCY(parameters)

    if methodname=='statnwzhy':
        rs=statnwzhy(parameters)

    if methodname=='bigentInc':
        rs=bigentInc(parameters)

    if methodname=='nwzmonth':
        rs=nwzmonth(parameters)

    if methodname=='getPoint':
        rs=getPoint(parameters)


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