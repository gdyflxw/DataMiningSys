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
};
//Django的X-CSRF保护机制*********************END

//设置datarange的时间
function setdr(divid,btime,etime){
    $('#'+divid).parent().attr('data-start-date', btime);
    $('#'+divid).parent().attr('data-end-date', etime);
    $('#'+divid).html(btime + ' - ' + etime);
};

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
};





function getDataTable(params,divid,filename,cols,summarys,tbdata=null,item='items'){
    if(tbdata==null){
    tbdata = $.ajax({
                url: "../apis/",
                dataType: "json",
                method:"POST",
                data: params,
                async:false,
                }).responseJSON
    };
    $("#"+divid).dxDataGrid({
        dataSource: tbdata[item],
        rowAlternationEnabled:true,
        allowColumnResizing:true,
        columnMinWidth:100,
        columnResizingMode:"widget",
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
            columnRenderingMode:"standard",
            rowRenderingMode:"standard"
        },
        columns:cols,
        summary:summarys
    }).dxDataGrid("instance");
    return tbdata;
};

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
};

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
};



//无分组功能，无导出功能
function getDataTable_NGE(params,divid,filename,cols,summarys,tbdata=null,item='items'){
    if(tbdata==null){
    var tbdata = $.ajax({
                url: "../apis/",
                dataType: "json",
                method:"POST",
                data: params,
                async:false,
                }).responseJSON
    }
    $("#"+divid).dxDataGrid({
        dataSource: tbdata[item],
        rowAlternationEnabled:true,
        allowColumnResizing:true,
        //columnMinWidth:120,
        columnResizingMode:"widget",
        showBorders:true,
        paging:{
            pageSize:20
        },
        scrolling:{
            columnRenderingMode:"standard",
            rowRenderingMode:"standard"
        },
        columns:cols,
        summary:summarys
    }).dxDataGrid("instance");
    return tbdata;
};

//内外资走势图
function spec_combCharts(divid,tbdata){
$("#"+divid).dxChart({
        dataSource: tbdata['items'],
        commonSeriesSettings:{
            argumentField: "统计月份s",
            label:{
                visible:true,
                backgroundColor:"none",
                connector:{
                    visible:true
                },
                font:{
                    color:"#666666"
                }                
            }
        },
        tooltip: {
            enabled: true,
            format: "fixedPoint"
        },
        panes: [{
                name: "cnt"
            }, {
                name: "cap"
            }
            ],
        defaultPane: "cap",
        onTooltipShown: function (e) {
            var point = e.target;
            // Handler of the "tooltipShown" event
        },
        onTooltipHidden: function (e) {
            var point = e.target;
            // Handler of the "tooltipHidden" event
        },
        series: [{ 
                pane: "cnt",
                type: "bar",
                valueField: "内资企业数量",
                name: "内资企业数量"
                
            }, {
                pane: "cnt", 
                type:"bar",
                valueField: "外资企业数量",
                name: "外资企业数量"                    
                
            }, {
                pane: "cap", 
                type:"line",
                valueField: "内资企业资金",
                name: "内资企业资金",
                label:{
                    font:{
                        size:10
                    },                
                    format:"thousands"
                }
            }, {
                //pane: "cap", 
                type:"line",
                valueField: "外资企业资金",
                name: "外资企业资金",
                label:{
                    font:{
                        size:10
                    },                
                    format:"thousands"
                }                   
                
            },
        ],    
        valueAxis: [{
            pane: "cnt",
            grid: {
                visible: true
            },
            autoBreaksEnabled: true,
            maxAutoBreakCount: 2
        }, {
            pane: "cap",
            grid: {
                visible: true
            },
            autoBreaksEnabled: true,
            maxAutoBreakCount: 2
        }],
        legend: {
            verticalAlignment: "bottom",
            horizontalAlignment: "center"            
        },
        onLegendClick: function (e) {
            var series = e.target;
            if (series.isVisible()) {
                series.hide();
            } else {
                series.show();
            }
        }
    });
};


function OD(a, b, c) {
    while (a > c) a -= c - b;
    while (a < b) a += c - b;
    return a;
};
function SD(a, b, c) {
    a = Math.max(a, b);
    a = Math.min(a, c);
    return a;
};
function getDistance(a_lng,a_lat,b_lng,b_lat) {
    var a = Math.PI * OD(a_lng, -180, 180) / 180;
    var b = Math.PI * OD(b_lng, -180, 180) / 180;
    var c = Math.PI * SD(a_lat, -74, 74) / 180;
    var d = Math.PI * SD(b_lat, -74, 74) / 180;
    return 6370996.81 * Math.acos(Math.sin(c) * Math.sin(d) + Math.cos(c) * Math.cos(d) * Math.cos(b-a));
};

function getsquare(lng,lat,r,type=null){
    lng=parseFloat(lng);
    lat=parseFloat(lat);
    r=parseFloat(r)/1.141;
    if(type=='json'){
        rst={"minlng":lng-r*1.02*0.00001,"maxlng":lng+r*1.02*0.00001,"minlat":lat-r*1.11*0.00001,"maxlat":lat+r*1.11*0.00001};
    }else{
        rst=[lng-r*1.02*0.00001,lng+r*1.02*0.00001,lat-r*1.11*0.00001,lat+r*1.11*0.00001]
    }
    return rst
};


//使用并保留小数点后两位，单位是米
//var m =getDistance(106.486654,29.490295,106.581515,29.615467).toFixed(2);




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
