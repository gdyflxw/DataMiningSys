import json
from lmf import db ,office_io


def db_query(sql):
    m=db()
    schema=m.db_query("select * from selectedschema",dbtype='postgresql',conp=['postgres','since2015','10.204.169.71','sist','public']).iat[0,0]
    df=m.db_query(sql,dbtype='postgresql',conp=['postgres','since2015','10.204.169.71','sist',schema])
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
    elif enttype1=='个体户':
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
        with m as (select distinct hy,hyname from base where ((zxdate between '%s' and '%s') or (zxdate between '%s' and '%s') or (zxdate between '%s' and '%s')) %s %s),
             a as (select hy,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by hyname,hy),
             b as (select hy,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by hyname,hy),
             c as (select hy,count(*) cn,sum(zczj_sp) sm from base where zxdate between '%s' and '%s' %s %s group by hyname,hy),
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