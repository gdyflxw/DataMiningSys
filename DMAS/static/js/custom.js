//Django的X-CSRF保护机制*********************BEGIN
$(function() {
    $.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
});

//getCookie函数：

function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
    if (arr = document.cookie.match(reg))
        return unescape(arr[2]);
    else
        return null;
}
//Django的X-CSRF保护机制*********************END


//获取同比环比的时间段，并返回object{nowdateB:'2018-05-01',nowdateE:'2018-05-31',lastdateB:'2018-04-01',
//lastdateE:'2018-04-31',lastYdateB:'2017-05-01',lastYdateE:'2017-05-31'}
//daterange格式：datebegin - dateend；年月日格式,若为整月，则为上一个月整月，若非整月，则使用时间段之差的天数作为同比环比差异
function getCompDate(nowdB,nowdE){
    moment.locale('cn');
    nowdateB=moment(nowdB,'YYYY-MM-DD');
    nowdateE=moment(nowdE,'YYYY-MM-DD');

    if (moment(nowdateB).isSame(moment(nowdateB).startOf('month'),'day') && moment(nowdateE).isSame(moment(nowdateE).endOf('month'),'day') && moment(nowdateB).isSame(moment(nowdateE),'months')){
        lastdateB=moment(nowdateB).subtract(1,'months').startOf('month');
        lastdateE=moment(nowdateE).subtract(1,'months').endOf('month');
        lastYdateB=moment(nowdateB).subtract(1,'years').startOf('month');
        lastYdateE=moment(nowdateE).subtract(1,'years').endOf('month');
    }
    else if(moment(nowdateB).isSame(moment(nowdateB).startOf('month'),'day') && moment(nowdateE).isSame(moment(nowdateE).endOf('month'),'day') && moment(nowdateB).isSame(moment(nowdateE),'quarter') && moment(nowdateE).diff(moment(nowdateB),'months')==2){
        lastdateB=moment(nowdateB).subtract(1,'quarters').startOf('month');
        lastdateE=moment(nowdateE).subtract(1,'quarters').endOf('month');
        lastYdateB=moment(nowdateB).subtract(1,'years').startOf('month');
        lastYdateE=moment(nowdateE).subtract(1,'years').endOf('month');
        alert ('1')
    }
    else if(moment(nowdateE).diff(moment(nowdateB),'days')<=20){
        dif=moment(nowdateE).diff(moment(nowdateB),'days')+1
        lastdateB=moment(nowdateB).subtract(dif,'days');
        lastdateE=moment(nowdateE).subtract(dif,'days');
        lastYdateB=moment(nowdateB).subtract(1,'months');
        lastYdateE=moment(nowdateE).subtract(1,'months');        
    }
    else{
        dif=moment(nowdateE).diff(moment(nowdateB),'days')+1
        lastdateB=moment(nowdateB).subtract(dif,'days');
        lastdateE=moment(nowdateE).subtract(dif,'days');
        lastYdateB=moment(nowdateB).subtract(1,'years');
        lastYdateE=moment(nowdateE).subtract(1,'years');   
    }
    return {"nowdateB":nowdateB.format('YYYY-MM-DD'),"nowdateE":nowdateE.format('YYYY-MM-DD'),"lastdateB":lastdateB.format('YYYY-MM-DD'),"lastdateE":lastdateE.format('YYYY-MM-DD'),"lastYdateB":lastYdateB.format('YYYY-MM-DD'),"lastYdateE":lastYdateE.format('YYYY-MM-DD')}
}





function getDataTable(params,divid,filename,cols,summarys){
    var tbdata = $.ajax({
                url: "../apis/",
                dataType: "json",
                method:"POST",
                data: params,
                async:false,
                }).responseJSON
    
    $("#"+divid).dxDataGrid({
        dataSource: tbdata.items,
        rowAlternationEnabled:true,
        showBorders:true,
        paging:{
            pageSize:10
        },
        groupPanel:{
            visible:true
        },
        "export":{
            enabled:true,
            fileName:filename
        },
        pager:{
            showPageSizeSelector:true,
            allowePageSizes:[5,10,20],
            showInfo:true
        },
        scrolling:{
            columnRenderingMode:"virtual"
        },
        columns:cols,
        summary:summarys
    }).dxDataGrid("instance");
    return tbdata;
}

function getPieChart(params,divid,filename,series,tbdata){
    if (tbdata==undefined) {
        tbdata=$.ajax({
                url: "../apis/",
                dataType: "json",
                method:"POST",
                data: params,
                async:false,
                }).responseJSON
    }    
    $("#"+divid).dxPieChart({
        palette:"harmony Light",
        dataSource:tbdata['items'],        
        title:{
            text:filename,
            font:{
                size:"20px"
            }
        },
        legend:{visible:false},
        resolveLabelOverlapping:"shift",
        "export":{
            enabled:true,
            fileName:filename
        },
        series:series,
    }).dxPieChart('instance')
    return tbdata;
}

function getZoomLine(params,ChartDivid,RangeDivid,series,tbdata){
    if(tbdata==undefined){
        tbdata=$.ajax({
                url: "../apis/",
                dataType: "json",
                method:"POST",
                data: params,
                async:false,
                }).responseJSON
    }
    $("#"+ChartDivid).dxChart({
        palette:"harmony Light",
        dataSource:tbdata['items'],
        commonSeriesSettings:{
            point:{
                size:7
            },
            type:"splinearea"
        },
        series:series,
        legend:{
            position:"inside",
            horizontalAlignment:"right",
            verticalAlignment:"top"
        }
    });
    $("#"+RangeDivid).dxRangeSelector({
        size:{
            height:100
        },
        margin:{
            left:10
        },
        dataSource:tbdata['items'],
        chart:{
            series:series,
            palette:"harmony Light",
            commonSeriesSettings:{
            type:"spline"
        }
        },
        behavior:{
            callValueChanged:"onMoning"
        },
        onValueChanged:function(e){
            var zoomedChart=$("#"+ChartDivid).dxChart("instance");
            zoomedChart.zoomArgument(e.value[0],e.value[1]);            
        }
    });
}





/*
*********原函数，使用Deffered提供数据交换，更合理，但因找不到数据共享方式，转而使用普通ajax方式*************
function getDataTableA(params,divid,filename,cols,summarys){
    var orders = new DevExpress.data.CustomStore({
        load: function (loadOptions) {
            var deferred = $.Deferred(),
                args = params;
            if (loadOptions.sort) {
                args.orderby = loadOptions.sort[0].selector;
                if (loadOptions.sort[0].desc)
                    args.orderby += " desc";
            }
    
            args.skip = loadOptions.skip || 0;
            args.take = loadOptions.take || 12;
            var ajaxdata=$.ajax({
                url: "../apis/",
                dataType: "json",
                method:"POST",
                data: args,
                success: function(result) {
                    deferred.resolve(result.items, { totalCount: result.totalCount,columnsname:result.columnsname });
                },
                error: function() {
                    deferred.reject("Data Loading Error");
                },
                timeout: 3000
            });            
            return deferred.promise();
        }
    });

    $("#"+divid).dxDataGrid({
        dataSource: {
            store: orders
        },
        rowAlternationEnabled:true,
        showBorders:true,
        paging:{
            pageSize:10
        },
        groupPanel:{
            visible:true
        },
        "export":{
            enabled:true,
            fileName:filename
        },
        pager:{
            showPageSizeSelector:true,
            allowePageSizes:[5,10,20],
            showInfo:true
        },
        scrolling:{
            columnRenderingMode:"virtual"
        },
        columns:cols,
        summary:summarys
    }).dxDataGrid("instance");
}
*/
