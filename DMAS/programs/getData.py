import json
from lmf import db ,office_io
import pandas as pd

def db_query(sql):
    m=db()
    #schema=m.db_query("select * from selectedschema",dbtype='postgresql',conp=['postgres','since2015','10.204.169.71','sist','public']).iat[0,0]
    df=m.db_query(sql,dbtype='postgresql',conp=['postgres','sist@123','10.204.169.17','postgres','sist20180602'])
    return df

def xzqhpmon(params):
    xzqh,begindate,enddate=params['xzqh'],params['begintime'],params['endtime']
    sql="select 行政区划, 截止日期, 商事主体总量, 企业数量, 企业占比, 个体数量, 个体占比 from state_tb_cun where 行政区划='%s' and 截止日期>='%s' and 截止日期<='%s'"%(xzqh,begindate,enddate)
    df=db_query(sql)
    df=df.sort_values(by='截止日期',ascending=False)
    df.fillna('',inplace=True)
    arr={"totalCount":len(df),"items":df.to_dict("records")}
    return arr

def monpxzqh(params):
    enddate,qianhai=params['endtime'],params['qianhai']
    if enddate[-2:]=='01':
        sql="""select 行政区划 as 区域 
            ,商事主体总量 as 主体总量
            ,企业数量 as 企业
            ,个体数量 as 个体  from state_tb_cun where 截止日期='%s' and 行政区划 not in ('全市','南山区')

        """%(enddate) if qianhai=='false' else """select 行政区划 as 区域 
            ,商事主体总量 as 主体总量
            ,企业数量 as 企业
            ,个体数量 as 个体  from state_tb_cun where 截止日期='%s' and 行政区划 not in ('全市','南山前海','南山非前海')
        """%(enddate)
    else:
        sql="""SELECT xzqh_sp 区域
            ,COUNT(*) 主体总量
            ,count(*) filter(where jglxdm in('1','2'))  企业
            ,count(*) filter(where jglxdm in('B')) 个体
            FROM base where clrq<'%s'
            and xzqh_sp in('宝安区','罗湖区','福田区','坪山区','龙华区','盐田区'
            ,'光明区','大鹏区','南山非前海','南山前海','龙岗区') and ztztdm>=0
            and jglxdm in('1','2','B')
            group by xzqh_sp"""%enddate if qianhai=='false' else """SELECT case when xzqh_sp in ('南山前海','南山非前海') then '南山区' else xzqh_sp end  区域
            ,COUNT(*) 主体总量
            ,count(*) filter(where jglxdm in('1','2'))  企业
            ,count(*) filter(where jglxdm in('B')) 个体
            FROM base where clrq<'%s'
            and xzqh_sp in('宝安区','罗湖区','福田区','坪山区','龙华区','盐田区'
            ,'光明区','大鹏区','南山非前海','南山前海','龙岗区') and ztztdm>=0
            and jglxdm in('1','2','B')
            group by case when xzqh_sp in ('南山前海','南山非前海') then '南山区' else xzqh_sp end"""%enddate
    
    df=db_query(sql)

    df['总量市占比']=(df['主体总量']/df['主体总量'].sum()).map(lambda x:round(x,4))
    df['企业市占比']=(df['企业']/df['企业'].sum()).map(lambda x:round(x,4))
    df['个体市占比']=(df['个体']/df['个体'].sum()).map(lambda x:round(x,4))

    df.fillna('',inplace=True)
    
    arr={"totalCount":len(df),"items":df.to_dict("records")}
    return arr

def dailyinc(params):
    xzqh,begindate,enddate=params['xzqh'],params['begintime'],params['endtime']
    if xzqh=='全市':
        s1=" "
    elif xzqh=='南山区':
        s1=" and xzqh_sp in('南山前海','南山非前海')"
    else:
        s1=" and xzqh_sp='%s'"%xzqh
    sql="""
        select x.clrq,COALESCE(y."all",0) as "all",COALESCE(y."ent",0) as "ent",COALESCE(y."per",0) as "per" from (
        SELECT to_char(T, 'yyyy-MM-DD') AS "clrq" FROM generate_series ( '%s' :: DATE, '%s' :: DATE, INTERVAL '1 day' ) T ) x
        left join ( SELECT clrq, sum(case when jglxdm in ('1','2','B') then 1 else 0 end ) as "all", sum(case when jglxdm in ('1','2') then 1 else 0 end ) as ent,
        sum(case when jglxdm in ('B') then 1 else 0 end ) as per FROM base WHERE clrq >= '%s' AND clrq <= '%s' %s GROUP BY clrq ) y
        on x.clrq=y.clrq
        """%(begindate,enddate,begindate,enddate,s1)
    df=db_query(sql)
    df.fillna('',inplace=True)
    df.rename(columns={"clrq":"成立日期","all":"商事主体","ent":"企业","per":"个体"},inplace=True)
    arr={"items":df.to_dict("records")}
    return arr

def monthlyinc(params):
    xzqh,begindate,enddate=params['xzqh'],params['begintime'],params['endtime']
    if xzqh=='全市各区':
        s1=" 行政区划!='全市' "
    else:
        s1=" 行政区划='%s' "%xzqh

    sql="""
        select * from state_tb_zeng where %s and 统计月份>='%s' and 统计月份<='%s' 
        """%(s1,begindate,enddate)
    df=db_query(sql)
    df.fillna('',inplace=True)    
    arr={"items":df.to_dict("records")}
    return arr

def cancelhy(params):
    xzqh,enttype,nowdateB,nowdateE,lastdateB,lastdateE,lastYdateB,lastYdateE=params['xzqh'],params['enttype'],params['nowdateB'],params['nowdateE'],params['lastdateB'],params['lastdateE'],params['lastYdateB'],params['lastYdateE']
    if enttype=='企业':
        jglxstr="and jglxdm in ('1','2')"
    elif enttype=='个体':
        jglxstr="and jglxdm in ('B')"
    else:
        jglxstr="and jglxdm in ('1','2','B')"
    if xzqh=='全市':
        xzqhstr=''
    elif xzqh=='南山区':
        xzqhstr="and xzqh_sp in('南山非前海','南山前海')  "
    else:
        xzqhstr="and xzqh_sp='%s'  "%xzqh
    sql="""
        with m as (select distinct hy,hyname from base where hy is not null and ((zxdate between '%s' and '%s') or (zxdate between '%s' and '%s') or (zxdate between '%s' and '%s')) %s %s),
             a as (select hy,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by hyname,hy),
             b as (select hy,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by hyname,hy),
             c as (select hy,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by hyname,hy)
        select m.hy as 行业门类代码,m.hyname as 行业门类,
        a.cn as 本期数量,
        a.sm as 本期金额,
        b.cn as 同比数量,
        b.sm as 同比金额,
        c.cn as 环比数量,
        c.sm as 环比金额
        from m left join a on m.hy=a.hy left join b on m.hy=b.hy left join c on m.hy=c.hy
        """%(nowdateB,nowdateE,lastdateB,lastdateE,lastYdateB,lastYdateE,jglxstr,xzqhstr,nowdateB,nowdateE,jglxstr,xzqhstr,lastdateB,lastdateE,jglxstr,xzqhstr,lastYdateB,lastYdateE,jglxstr,xzqhstr)
    df=db_query(sql)
    df.fillna('',inplace=True)
    arr={"items":df.to_dict("records")}
    return arr

def cancelqh(params):
    xzqh,enttype,nowdateB,nowdateE,lastdateB,lastdateE,lastYdateB,lastYdateE=params['xzqh'],params['enttype'],params['nowdateB'],params['nowdateE'],params['lastdateB'],params['lastdateE'],params['lastYdateB'],params['lastYdateE']
    sql=""
    if enttype=='企业':
        jglxstr="and jglxdm in ('1','2')"
    elif enttype=='个体':
        jglxstr="and jglxdm in ('B')"
    else:
        jglxstr="and jglxdm in ('1','2','B')"
    if xzqh=='全市':
        xzqhstr=""
        sql="""
            with m as (select distinct xzqh_sp from base where xzqh_sp is not null and ((zxdate between '%s' and '%s') or (zxdate between '%s' and '%s') or (zxdate between '%s' and '%s')) %s %s),
                 a as (select xzqh_sp,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by xzqh_sp),
                 b as (select xzqh_sp,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by xzqh_sp),
                 c as (select xzqh_sp,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by xzqh_sp)
            select m.xzqh_sp as 区域,
            a.cn as 本期数量,
            a.sm as 本期金额,
            b.cn as 同比数量,
            b.sm as 同比金额,
            c.cn as 环比数量,
            c.sm as 环比金额
            from m left join a on m.xzqh_sp=a.xzqh_sp left join b on m.xzqh_sp=b.xzqh_sp left join c on m.xzqh_sp=c.xzqh_sp
            """%(nowdateB,nowdateE,lastdateB,lastdateE,lastYdateB,lastYdateE,jglxstr,xzqhstr,nowdateB,nowdateE,jglxstr,xzqhstr,lastdateB,lastdateE,jglxstr,xzqhstr,lastYdateB,lastYdateE,jglxstr,xzqhstr)
    elif xzqh=='南山区':
        xzqhstr="and xzqh_sp in('南山非前海','南山前海')  "
    else:
        xzqhstr="and xzqh_sp='%s'  "%xzqh
    if sql=="":
        sql="""
            with m as (select distinct jd from base where jd is not null and ((zxdate between '%s' and '%s') or (zxdate between '%s' and '%s') or (zxdate between '%s' and '%s')) %s %s),
                 a as (select jd,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by jd),
                 b as (select jd,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by jd),
                 c as (select jd,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by jd)
            select m.jd as 区域,
            a.cn as 本期数量,
            a.sm as 本期金额,
            b.cn as 同比数量,
            b.sm as 同比金额,
            c.cn as 环比数量,
            c.sm as 环比金额
            from m left join a on m.jd=a.jd left join b on m.jd=b.jd left join c on m.jd=c.jd
            """%(nowdateB,nowdateE,lastdateB,lastdateE,lastYdateB,lastYdateE,jglxstr,xzqhstr,nowdateB,nowdateE,jglxstr,xzqhstr,lastdateB,lastdateE,jglxstr,xzqhstr,lastYdateB,lastYdateE,jglxstr,xzqhstr)    
    df=db_query(sql)
    df.fillna('',inplace=True)
    arr={"items":df.to_dict("records")}
    return arr

def canceldt(params):
    xzqh,enttype,nowdateB,nowdateE=params['xzqh'],params['enttype'],params['nowdateB'],params['nowdateE']
    if enttype=='企业':
        jglxstr="and jglxdm in ('1','2')"
    elif enttype=='个体':
        jglxstr="and jglxdm in ('B')"
    else:
        jglxstr="and jglxdm in ('1','2','B')"
    if xzqh=='全市':
        xzqhstr=''
    elif xzqh=='南山区':
        xzqhstr="and xzqh_sp in('南山非前海','南山前海')  "
    else:
        xzqhstr="and xzqh_sp='%s'  "%xzqh
    sql="""
        select
        ztsfdm 企业号,jgdm 机构代码,zch 注册号,tydm  统一社会信用代码,jgmc 企业名称,jglx 机构类型,fddbr 法定代表人,
        clrq 注册日期,jgdz 注册地址,zczj 注册资金,hbzl 货币种类,zczj_sp 注册资金_人民币,zgrs 职工人数,
        x1.jjhydm 经济行业小类代码,x2.jjhy 经济行业小类,hy 经济行业门类代码,hyname 经济行业门类,qylx  企业类型,
        nwz 内外资,gb 投资国别,sh 股东,jyfw 经营范围,jd 街道,xzqh_sp 行政区划,zxdate 注吊销时间
        from  base x1 left join dict_jjhy x2 on  x1.jjhydm=x2.jjhydm
        where zxdate between '%s' and '%s' %s  %s
        """%(nowdateB,nowdateE,jglxstr,xzqhstr)
    df=db_query(sql)
    df.fillna('',inplace=True)
    arr={"items":df.to_dict("records")}
    return arr


def SrvIndhy(params):
    xzqh,begindate,enddate=params['xzqh'],params['nowdateB'],params['nowdateE']
    if xzqh=='全市':xzqhstr=''
    elif xzqh=='南山区':xzqhstr=" and xzqh_sp in('南山非前海','南山前海')"
    else:xzqhstr=" and xzqh_sp='%s'"%xzqh
    sql="""
        with og as (select ztsfdm,zczj_sp,
        CASE SUBSTRING (jjhydm, 2, 3)
        WHEN '723' THEN '咨询与调查'
        WHEN '722' THEN '法律服务'
        WHEN '721' THEN '企业管理服务'
        WHEN '729' THEN '其他商务服务'
        WHEN '725' THEN '知识产权服务'
        WHEN '752' THEN '科技中介服务'
        ELSE '文化艺术经纪代理'
        END AS newhy
        FROM base WHERE clrq BETWEEN '%s' AND '%s'
        AND jglxdm IN ('1', '2')
        AND SUBSTRING (jjhydm, 2, 3) IN (   '723',  '722',  '721',  '729',  '725',  '752',  '894') %s)
        select newhy as "专门专业服务业名称" ,count(*) "企业数量（单位：家）" ,sum(zczj_sp) "注册资金（单位：万元）"  
        from og group by newhy
        order by count(*) desc
    """%(begindate,enddate,xzqhstr)
    df=db_query(sql)
    df.fillna('',inplace=True)
    arr={"items":df.to_dict("records")}
    return arr


def SrvIndqh(params):
    xzqh,begindate,enddate=params['xzqh'],params['nowdateB'],params['nowdateE']
    if xzqh=='全市':xzqhstr=''
    elif xzqh=='南山区':xzqhstr=" and xzqh_sp in('南山非前海','南山前海')"
    else:xzqhstr=" and xzqh_sp='%s' "%xzqh
    sql="""
        with og as (select ztsfdm,jd,zczj_sp
        FROM base WHERE clrq BETWEEN '%s' AND '%s'
        AND jglxdm IN ('1', '2')
        AND SUBSTRING (jjhydm, 2, 3) IN ('723',  '722',  '721',  '729',  '725',  '752',  '894') %s)
        select jd as "街道" ,count(*) "企业数量（单位：家）" ,sum(zczj_sp) "注册资金（单位：万元）"  
        from og group by jd
        order by count(*) desc
    """%(begindate,enddate,xzqhstr)
    df=db_query(sql)
    df.fillna('',inplace=True)
    arr={"items":df.to_dict("records")}
    return arr

def StatCY(params):
    nwz,xzqh,begindate,enddate=params['nwz'],params['xzqh'],params['nowdateB'],params['nowdateE']
    if nwz=='外资':
        nwzstr="and nwz='外资'"
    else:
        nwzstr="and nwz='内资' and lyd <> '深圳本土'"
    if xzqh=='全市':xzqhstr=''
    elif xzqh=='南山区':xzqhstr="xzqh_sp in('南山非前海','南山前海') and "
    else:xzqhstr=" and xzqh_sp='%s' "%xzqh
    sql="""select zczj_sp,
        case when substr(jjhydm,2,5) in(
        '3911','3912','3913','3919','3921','3922','3931','3932','3940','3951','3952','3953','3961','3962','3963','3969','3971','3972'
        ,'3311','3412','3421','3431','3432','3433','3434','3467','3471','3473','3475','3479','4019','4021','4022','4023','4025','4026','4027'
        ,'4028','4029','4041','4090','4330','4350','4360'
        ,'3610','3620','3630','3660','3711','3713','3741','3742','4343','3542','3545','3561','3562','3591','3595','3720','3743','3811','3812','3819'
        ,'3821','3822','3823','3824','3825','3829','3831','3833','3839','3841','3842','3849','3871','3879','3891','3899','4011','4012','4013','4014','4015'
        ,'2710','2720','2740','2750','2760','2770','3581','3583','3584','3586'
        ,'1320','1495','2330','2632','2651','2652','2653','2661','2664','2911','3024','3052') then 1 else 0 end as xdzz,
        case when jgmc ~'船舶制造|航天.*科技|海洋工程|轨道交通|卫星' or jyfw ~'船舶制造|航天.*科技|海洋工程|轨道交通|智能装备' then 1 else 0 end as gdzb,
        case when substr(jjhydm,1,1)='C' then 1 else 0 end as zzy,
        case when substr(jjhydm,1,1) not in ('A','B','C','D','E') then 1 else 0 end as fwy,
        case when substr(jjhydm,1,3) in ('I63','I64','I65','J66','J67','J68','J69','K70','L72','M73','M74','M75','N77','P82','Q83','R85','R86','R87','R88','R89','S93') then 1 else 0 end as xdfw,
        case when jgmc ~'生物' or jyfw ~'生物.*生物|生物技术\S发|生物科技' then '生物产业'
             when jgmc ~'环保|节能' or jyfw ~'节能.*环保|环保设备|环保检测|再生资源|环保工程|环保.*环保|节能.*节能' then '节能环保'
             when jgmc ~'船舶制造|航天.*科技|海洋工程|轨道交通|卫星' or jyfw ~'船舶制造|航天.*科技|海洋工程|轨道交通|智能装备' then '高端装备业'
             when jgmc ~'新能源[^汽]|能源[^汽]' or jyfw ~'新能源[^汽]' then '新能源'
             when jgmc ~'云计算|信息安全|大数据|操作系统|高端软件' or jyfw ~'云计算|信息安全|大数据|操作系统|高端软件|大型数据库' then '新一代信息技术'
             when jgmc ~'新材料' or jyfw ~'高分子|硅.*材料|稀土|树脂|高性能\S料|无机非金属|有机.{1,3}材料' then '新材料产业'
             when jgmc ~'新能源汽车|电力汽车' or jyfw~ '新能源汽车' then '新能源汽车'
             else '其它' end as zlxx,
        case when substr(jjhydm,2,4) in
                    ('7233','7250','7294','8941','8949','7121','7122','7123','7299','7272','7279','7851','7852','7840','7711','7712','7713',
                    '8911','8912','8913','8919','8920','8830','8990','7492','2411','2412','2414','2421','2422','2423','2429','2450','2672',
                    '2221','2222','2642','2643','2664','3872','3990','3471','3472','3473','3474','3479','3542','3931','3932','3939','3951',
                    '3952','3953','2461','2462','2469','7212','8710','8720','8731','8732','8740','8750','8760','2311','2312','2319','2320',
                    '2330','5141','5241','5247','5248','5137','5271','5149','5249','5178','5176','5272','8293','8241','8299','8790','8770',
                    '7350','9421','8510','8521','8522','8523','8524','8525','8529','5143','5144','5145','5243','5244','5294','8610','8620',
                    '6321','6322','6330','8630','8640','8650','8660','6510','6591','6319','6410','6420','6420','6490','6520','6530','7240',
                    '7292','3079','5182','5181','5146','5245','5246','7482','7483','7491','6550','6550','7271') or substr(jjhydm,2,3)= '243' then '文化创意' else '其它' end as whcy ,
        case when jgmc ~'互联网' or jyfw ~'互联网' then '互联网产业' else '其它' end as hlw
        from base where jglxdm in ('1','2') and clrq between '%s' and '%s' %s %s"""%(begindate,enddate,nwzstr,xzqhstr)
    df=db_query(sql)
    zzydf=pd.DataFrame({nwz+"制造业":['先进制造业','传统制造业'],
        "数量":[
            len(df.loc[(df['xdzz']==1) | (df['gdzb']==1),('zczj_sp')]), 
            len(df.loc[(df['zzy']==1) & (df['xdzz']!=1),('zczj_sp')])],
        "注册资金":[
        sum(df.loc[(df['xdzz']==1) | (df['gdzb']==1),('zczj_sp')]),
        sum(df.loc[(df['zzy']==1) & (df['xdzz']!=1),('zczj_sp')])]})
    zzydf['数量占比']=zzydf['数量'].map(lambda x: round(x/sum(zzydf['数量']),4))
    zzydf['资金占比']=zzydf['注册资金'].map(lambda x: round(x/sum(zzydf['注册资金']),4))

    fwydf=pd.DataFrame({nwz+"服务业":['先进服务业','传统服务业'],
        "数量":[
            len(df.loc[(df['xdfw']==1),('zczj_sp')]), 
            len(df.loc[(df['fwy']==1) & (df['xdfw']!=1),('zczj_sp')])],
        "注册资金":[
        sum(df.loc[(df['xdfw']==1),('zczj_sp')]),
        sum(df.loc[(df['fwy']==1) & (df['xdfw']!=1),('zczj_sp')])]})
    fwydf['数量占比']=fwydf['数量'].map(lambda x: round(x/sum(fwydf['数量']),4))
    fwydf['资金占比']=fwydf['注册资金'].map(lambda x: round(x/sum(fwydf['注册资金']),4))
    
    zlxxdf=df.loc[df['zlxx']!='其它',['zlxx','zczj_sp']].groupby(['zlxx'],as_index=False).count().merge(df.loc[df['zlxx']!='其它',['zlxx','zczj_sp']].groupby(['zlxx'],as_index=False).sum(),on='zlxx')
    zlxxdf=zlxxdf.rename(columns={'zlxx':nwz+'战略新兴产业','zczj_sp_x':'数量','zczj_sp_y':'注册资金'})
    zlxxdf['数量占比']=zlxxdf['数量'].map(lambda x: round(x/sum(zlxxdf['数量']),4))
    zlxxdf['资金占比']=zlxxdf['注册资金'].map(lambda x: round(x/sum(zlxxdf['注册资金']),4))

    def c(x,y,z):
        if x!='其它':return x
        if y!='其它':return y
        return z
    df2=df.loc[(df['zlxx']!='其它')|(df['hlw']=='互联网产业')|(df['whcy']=='文化创意'),['zlxx','whcy','hlw','zczj_sp']]
    df2['comb']=df2.apply(lambda x:c(x.zlxx,x.whcy,x.hlw),axis=1)
    cydf=df2.loc[:,['comb','zczj_sp']].groupby(['comb'],as_index=False).count().merge(df2.loc[:,['comb','zczj_sp']].groupby(['comb'],as_index=False).sum(),on='comb')
    cydf=cydf.rename(columns={'comb':nwz+'新战略新兴产业','zczj_sp_x':'数量','zczj_sp_y':'注册资金'})
    cydf['数量占比']=cydf['数量'].map(lambda x: round(x/sum(cydf['数量']),4))
    cydf['资金占比']=cydf['注册资金'].map(lambda x: round(x/sum(cydf['注册资金']),4))

    arr={"zzy":zzydf.to_dict("records"),"fwy":fwydf.to_dict("records"),"zlxx":zlxxdf.to_dict("records"),"cy":cydf.to_dict("records")}
    return arr

def statnwzhy(params):
    xzqh,begindate,enddate=params['xzqh'],params['nowdateB'],params['nowdateE']
    if xzqh=='全市':xzqhstr=''
    elif xzqh=='南山区':xzqhstr=" and xzqh_sp in('南山非前海','南山前海')"
    else:xzqhstr=" and xzqh_sp='%s' "%xzqh
    sql="""
        select
        coalesce(hyname,'批发和零售业') 行业门类
        ,count(*) 企业数
        ,0 行业占比
        ,count(*) filter(where nwz!='外资') 内资企业数
        ,count(*) filter(where nwz='外资') 外资企业数
        ,count(*) filter(where nwz='外资' and zczj_sp>=3400) 五百万美元以上外资
        ,count(*) filter(where nwz='外资' and zczj_sp>=6800) 一千万美元以上外资
        ,count(*) filter(where nwz='内资' and zczj_sp>=10000) 一亿以上内资
        from base
        where jglxdm in('1','2') and clrq between '%s' and '%s' %s
        group by coalesce(hyname,'批发和零售业')
        order by 企业数 desc
    """%(begindate,enddate,xzqhstr)
    df=db_query(sql)
    su=sum(df['企业数'])
    df['行业占比']=round(df['企业数']/su,4)
    df.fillna('',inplace=True)
    arr={"items":df.to_dict("records")}
    return arr

def bigentInc(params):
    xzqh,nowdateB,nowdateE,lastdateB,lastdateE,lastYdateB,lastYdateE=params['xzqh'],params['nowdateB'],params['nowdateE'],params['lastdateB'],params['lastdateE'],params['lastYdateB'],params['lastYdateE']
    if xzqh=='全市':xzqhstr=''
    elif xzqh=='南山区':xzqhstr=" and xzqh_sp in('南山非前海','南山前海')"
    else:xzqhstr=" and xzqh_sp='%s' "%xzqh
    sql="""
        select a.*,b.环比数量,b.环比金额,c.同比数量,c.同比金额 from (
        select '内资(大于1亿)' 项目 ,count(*) 本期数量,(sum(zczj_sp)/10000)::numeric(20,4) 本期金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='内资' and zczj_sp>=10000 %s
        union all select '外资(大于500万美元)' 项目 ,count(*) 本期数量,(sum(zczj_sp)/10000)::numeric(20,4) 本期金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='外资' and zczj_sp>=3400 %s
        union all select '外资(大于1000万美元)' 项目 ,count(*) 本期数量,(sum(zczj_sp)/10000)::numeric(20,4) 本期金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='外资' and zczj_sp>=6800 %s
        ) a join (
        select '内资(大于1亿)' 项目 ,count(*) 环比数量,(sum(zczj_sp)/10000)::numeric(20,4) 环比金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='内资' and zczj_sp>=10000 %s
        union all select '外资(大于500万美元)' 项目 ,count(*) 环比数量,(sum(zczj_sp)/10000)::numeric(20,4) 环比金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='外资' and zczj_sp>=3400 %s
        union all select '外资(大于1000万美元)' 项目 ,count(*) 环比数量,(sum(zczj_sp)/10000)::numeric(20,4) 环比金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='外资' and zczj_sp>=6800 %s
        ) b on a.项目=b.项目 join (
        select '内资(大于1亿)' 项目 ,count(*) 同比数量,(sum(zczj_sp)/10000)::numeric(20,4) 同比金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='内资' and zczj_sp>=10000 %s
        union all select '外资(大于500万美元)' 项目 ,count(*) 同比数量,(sum(zczj_sp)/10000)::numeric(20,4) 同比金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='外资' and zczj_sp>=3400 %s
        union all select '外资(大于1000万美元)' 项目 ,count(*) 同比数量,(sum(zczj_sp)/10000)::numeric(20,4) 同比金额 from base where jglxdm in('1','2') and clrq between '%s' and '%s' and nwz='外资' and zczj_sp>=6800 %s
        ) c on a.项目=c.项目
    """%(nowdateB,nowdateE,xzqhstr,nowdateB,nowdateE,xzqhstr,nowdateB,nowdateE,xzqhstr,lastdateB,lastdateE,xzqhstr,lastdateB,lastdateE,xzqhstr,lastdateB,lastdateE,xzqhstr,lastYdateB,lastYdateE,xzqhstr,lastYdateB,lastYdateE,xzqhstr,lastYdateB,lastYdateE,xzqhstr)
    df=db_query(sql)
    df['环比数量增幅']=df.apply(lambda x: round(float((x.本期数量-x.环比数量)/x.环比数量),4) if x.环比数量>0 else '/',axis=1)
    df['环比金额增幅']=df.apply(lambda x: round(float((x.本期金额-x.环比金额)/x.环比金额),4) if x.环比金额>0 else '/',axis=1)
    df['同比数量增幅']=df.apply(lambda x: round(float((x.本期数量-x.同比数量)/x.同比数量),4) if x.同比数量>0 else '/',axis=1)
    df['同比金额增幅']=df.apply(lambda x: round(float((x.本期金额-x.同比金额)/x.同比金额),4) if x.同比金额>0 else '/',axis=1)
    
    arr={"items":df.to_dict("records")}
    return arr    

def nwzmonth(params):
    xzqh,begindate,enddate=params['xzqh'],params['nowdateB'],params['nowdateE']

    sql="""select * from state_tb_nwz where 行政区划='%s' and 统计月份>='%s' and 统计月份<='%s' """%(xzqh,begindate[:7],enddate[:7])
    df=db_query(sql)
    df['统计月份s']=df['统计月份'].map(lambda x:x.replace('-','')[2:])
    df.fillna('',inplace=True)
    arr={"items":df.to_dict('records')}
    return arr

def getPoint(params):
    minlng,maxlng,minlat,maxlat=params['minlng'],params['maxlng'],params['minlat'],params['maxlat']
    sql="""select b.jgmc,a.jgdz,lng,lat from sist20180602.lltmp a join sist20180602.base b on a.jzbh=b.jzbh where b.jglxdm in ('1','2') and lng between %s and %s and lat between %s and %s"""%(minlng,maxlng,minlat,maxlat)
    sqlh="""WITH a AS (
        select b.jgmc,a.jgdz,lng,lat from sist20180602.lltmp a join sist20180602.base b on a.jzbh=b.jzbh 
        where b.jglxdm in ('1','2') and a."lng" between %s and %s and a."lat" between %s and %s ) 
        select round(a.lng::numeric,4) AS lng,round(a.lat::numeric,4) as lat,count(*) as count from a  group by round(a.lng::numeric,4) ,round(a.lat::numeric,4) order by count desc
        """%(minlng,maxlng,minlat,maxlat)
    df=db_query(sql)
    df2=db_query(sqlh)
    arr={"items":df.to_dict('records'),"hotmap":df2.to_dict('records')}
    return arr


#模板
def templeteFunc(params):
    xzqh,begindate,enddate=params['xzqh'],params['nowdateB'],params['nowdateE']
    arr={"items":[]}
    return arr




