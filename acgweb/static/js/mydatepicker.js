Date.prototype.format =function(format)
{
    var o = {
        "M+" : this.getMonth()+1, //month
        "d+" : this.getDate(), //day
        "h+" : this.getHours(), //hour
        "m+" : this.getMinutes(), //minute
        "s+" : this.getSeconds(), //second
        "q+" : Math.floor((this.getMonth()+3)/3), //quarter
        "S" : this.getMilliseconds() //millisecond
    };
    if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
    (this.getFullYear()+"").substr(4- RegExp.$1.length));
    for(var k in o)if(new RegExp("("+ k +")").test(format))
    format = format.replace(RegExp.$1,
    RegExp.$1.length==1? o[k] :
    ("00"+ o[k]).substr((""+ o[k]).length));
    return format;
};

var starttime = parseInt($('#starttime_hidden').val());
if (starttime)
    $('#starttime_timepicker').val( new Date(parseInt(starttime) * 1000).format('yyyy-MM-dd'));

var endtime = parseInt($('#endtime_hidden').val());
if (endtime)
    $('#endtime_timepicker').val( new Date(parseInt(endtime - 24 * 3600) * 1000).format('yyyy-MM-dd'));

var VAR_SEMASTER_BASE = parseInt($("#VAR_SEMASTER_BASE").html());
var start_date = new Date(1000 * VAR_SEMASTER_BASE);
var end_date = new Date(1000 * (VAR_SEMASTER_BASE + 25 * 7 * 24 * 3600));

var now_time = new Date().getTime()/1000;
now_time = Math.floor ( ( now_time + 8 * 3600 ) / 86400 ) * 86400 - 8 * 3600 ;
//console.log(now_time);

$('.class_starttime_timepicker').datetimepicker({
    language: 'zh-CN',
    format: "yyyy-mm-dd",
    pickerPosition: "bottom-left",
    startDate: start_date.format("yyyy-MM-dd"),
    endDate: end_date.format("yyyy-MM-dd"),
	autoclose: 1,
	todayHighlight: 1,
	startView: 2,
	minView: 2,
	forceParse: 1,
    initialDate: new Date(now_time*1000)
}).on('changeDate', function(ev){
    $('#starttime_hidden').val( ev.date.valueOf()/1000 - 8 * 3600);
    //console.log(ev.date.toLocaleString());
});


$('.class_endtime_timepicker').datetimepicker({
    language: 'zh-CN',
    format: "yyyy-mm-dd",
    pickerPosition: "bottom-left",
    startDate: start_date.format("yyyy-MM-dd"),
    endDate: end_date.format("yyyy-MM-dd"),
    endDate: new Date(),
	autoclose: 1,
	todayHighlight: 1,
	startView: 2,
	minView: 2,
	forceParse: 1,
    initialDate:new Date(now_time*1000)
}).on('changeDate', function(ev){
    $('#endtime_hidden').val( ev.date.valueOf()/1000 - 8 * 3600 + 24 * 3600);
    //console.log(ev.date.toLocaleString());
});

