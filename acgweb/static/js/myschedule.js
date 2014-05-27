function parsemystr(str) {
    rtnlist = [];
    tmp1 = str.split(',');
    console.log('tmp1',tmp1);
    for (i in tmp1) {
        tmp2 = tmp1[i].split('-');
        console.log(tmp1[i],'tmp2',tmp2);
        if (tmp2.length==2) {
            for (j=parseInt(tmp2[0]);j<=parseInt(tmp2[1]);j++)
                rtnlist.push(j);
        }
        else
            rtnlist.push(parseInt(tmp1[i]));
    }
    return rtnlist;
}

function update_select() {

    $(".chk-week").each(function(){
        console.log(this);
        this.checked=0;
    });
    var weeklist = parsemystr($('#sch-week-input').val());
    console.log(weeklist);
    for (week in weeklist) {
        console.log(weeklist[week]);
        $(".chk-week")[(weeklist[week]-1)].checked=1;
    }

    $(".chk-weekday").each(function(){
        console.log(this);
        this.checked=0;
    });
    var weekdaylist = parsemystr($('#sch-weekday-input').val());
    console.log(weekdaylist);
    for (weekday in weekdaylist) {
        console.log(weekdaylist[weekday]);
        $(".chk-weekday")[(weekdaylist[weekday])].checked=1;
    }

    $(".chk-section").each(function(){
        console.log(this);
        this.checked=0;
    });
    var sectionlist = parsemystr($('#sch-section-input').val());
    console.log(sectionlist);
    for (section in sectionlist) {
        console.log(sectionlist[section]);
        $(".chk-section")[(sectionlist[section]-1)].checked=1;
    }

}

function update_input() {
    var str = '';
    var i = 0, val = 0, last_val = 0;
    var start = 0, end = 0;

    $(".chk-week").each(function(){
        last_val = val;
        val = this.checked;
        if (val && !last_val) {//posedge
            start = i+1;
        }
        else if (!val && last_val) {//negedge
            end = i;
            if (start == end)
                str += start+',';
            else
                str += start+'-'+end+',';
        }
        i += 1;
    });
    console.log(str.substr(0,str.length -1));
    $('#sch-week-input').val(str.substr(0,str.length -1))

    var str = '';
    var i = 0, val = 0, last_val = 0;
    var start = 0, end = 0;

    $(".chk-weekday").each(function(){
        last_val = val;
        val = this.checked;
        if (val && !last_val) {//posedge
            start = i;
        }
        else if (!val && last_val) {//negedge
            end = i-1;
            if (start == end)
                str += start+',';
            else
                str += start+'-'+end+',';
        }
        i += 1;
    });
    console.log(str.substr(0,str.length -1));
    $('#sch-weekday-input').val(str.substr(0,str.length -1))

    var str = '';
    var i = 0, val = 0, last_val = 0;
    var start = 0, end = 0;

    $(".chk-section").each(function(){
        last_val = val;
        val = this.checked;
        if (val && !last_val) {//posedge
            start = i+1;
        }
        else if (!val && last_val) {//negedge
            end = i;
            if (start == end)
                str += start+',';
            else
                str += start+'-'+end+',';
        }
        i += 1;
    });
    console.log(str.substr(0,str.length -1));
    $('#sch-section-input').val(str.substr(0,str.length -1))

}

$('#sch-week-input').change(function(){update_select();});
$('#sch-weekday-input').change(function(){update_select();});
$('#sch-section-input').change(function(){update_select();});

$('.chk-week').change(function(){update_input();});
$('.chk-weekday').change(function(){update_input();});
$('.chk-section').change(function(){update_input();});

update_select();