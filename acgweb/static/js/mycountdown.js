
var cntdwn = $('#activity_from_time_int').html();

function timer_run()
{

    cntdwn -= 1;
    if (cntdwn <= 0) {
        $('#activity_from_time_str').html('活动正在进行中');
    }
    else {

        var day = Math.floor(cntdwn / (24 * 60 * 60));
        var hour = Math.floor(cntdwn % (24 * 60 * 60) / ( 60 * 60 ));
        var minu = Math.floor(cntdwn % (60 * 60 ) / 60 );
        var sec = Math.floor(cntdwn % 60 );
        $('#activity_from_time_str').html('距活动开始还有 '+day+'天'+hour+'小时'+minu+'分'+sec+'秒');

        setTimeout(timer_run, 1000);
    }
}


timer_run();

