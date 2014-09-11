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
    }
    if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
    (this.getFullYear()+"").substr(4- RegExp.$1.length));
    for(var k in o)if(new RegExp("("+ k +")").test(format))
    format = format.replace(RegExp.$1,
    RegExp.$1.length==1? o[k] :
    ("00"+ o[k]).substr((""+ o[k]).length));
    return format;
}


$('.modal-trigger').click(function(){
    //console.log($(this));
    var colorlist = ['success','danger','default','warning','primary']
    for (color in colorlist){
        //ole.log(colorlist[color]);
        if ($(this).hasClass('btn-'+colorlist[color]))
            $('#myModalButton').addClass('btn-'+colorlist[color]);
    }
    $('#myModalLabel').html($(this).data('label'));
    $('#myModalContent').html($(this).data('content'));
    $('#myModalButton').html($(this).html());
    $('#myModalButton').data('loading-text', $(this).data('modal-loading-text'));
    //$('#myModalButton').attr('href',$(this).data('href'));
    if ($(this).data('require_input')) $('#myModalInput').show();
    else $('#myModalInput').hide()
    $('#myModalform').attr('action',$(this).data('href'));
    if ($(this).data('require_select')) {
        $('#myModalSelect').html('');
        var base_time = $(this).data('start_time');
        var i=1;
        for(i=1;i<13;i++){
            var time = base_time+i*30*60;
            var timeobj = new Date(time*1000);
            var timestr = timeobj.format('hh:mm');
            $('#myModalSelect').append('<option value="'+time+'">'+timestr+'</option>\n');
        }
        $('#myModalSelect').show()
    }
    else
        $('#myModalSelect').hide()

});
