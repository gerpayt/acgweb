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


var workstarttime = parseInt($('#form_workstarttime_hidden').val());
$('#form_workstarttime_timepicker').val(new Date(parseInt(workstarttime) * 1000).format('hh:mm'));

var starttime = parseInt($('#form_starttime_hidden').val());
$('#form_date_timepicker').val( new Date(parseInt(starttime) * 1000).format('yyyy-MM-dd'));
$('#form_starttime_timepicker').val( new Date(parseInt(starttime) * 1000).format('hh:mm'));

var endtime = parseInt($('#form_endtime_hidden').val());
if (endtime)
    $('#form_endtime_timepicker').val( new Date(parseInt(endtime) * 1000).format('hh:mm'));

var VAR_SEMESTER_BASE = parseInt($("#VAR_SEMESTER_BASE").html());
var start_date = new Date(1000 * VAR_SEMESTER_BASE);
var end_date = new Date(1000 * (VAR_SEMESTER_BASE + 25 * 7 * 24 * 3600));

$('.form_date').datetimepicker({
    language: 'zh-CN',
    format: "yyyy-mm-dd",
    pickerPosition: "bottom-left",
    startDate: start_date.format("yyyy-MM-dd"),
    endDate: end_date.format("yyyy-MM-dd"),
	autoclose: 1,
	todayHighlight: 1,
	startView: 2,
	minView: 2,
	forceParse: 1
}).on('changeDate', function(ev){
    var date = ev.date.valueOf()/1000;
    var stime = $('#form_starttime_hidden').val() % 86400;
    $('#form_starttime_hidden').val(date+stime);
    var work_stime = $('#form_workstarttime_hidden').val() % 86400;
    $('#form_workstarttime_hidden').val(date+work_stime);
    if ($('#form_endtime_hidden').val()) {
        etime = $('#form_endtime_hidden').val() % 86400;
        $('#form_endtime_hidden').val(date+etime);
    }
});

$('#form_workstarttime_timepicker').timepicker({
    minuteStep: 30,
    showInputs: true,
    showMeridian: false,
    defaultTime: false
}).on('changeTime.timepicker', function(ev) {
    var date = Math.floor($('#form_starttime_hidden').val() / 86400 ) * 86400;
    var time = ev.time.hours*3600 + ev.time.minutes*60 ;
    $('#form_workstarttime_hidden').val(date+time -8*3600)
});

$('#form_starttime_timepicker').timepicker({
    minuteStep: 30,
    showInputs: true,
    showMeridian: false,
    defaultTime: false
}).on('changeTime.timepicker', function(ev) {
    var date = Math.floor($('#form_starttime_hidden').val() / 86400 ) * 86400;
    var time = ev.time.hours*3600 + ev.time.minutes*60;
    $('#form_starttime_hidden').val(date+time -8*3600);
});

$('#form_endtime_timepicker').timepicker({
    minuteStep: 30,
    showInputs: true,
    showMeridian: false,
    defaultTime: false
}).on('changeTime.timepicker', function(ev) {
    var date = Math.floor($('#form_starttime_hidden').val() / 86400 ) * 86400;
    var time = ev.time.hours*3600 + ev.time.minutes*60;
    $('#form_endtime_hidden').val(date+time -8*3600);
});

$('#form_endtime_cancel').click(function(){
    $('#form_endtime_hidden').val(0);
    $('#form_endtime_timepicker').timepicker('setTime', '');
});
