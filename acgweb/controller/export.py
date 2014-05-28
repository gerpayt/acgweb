# coding: utf-8
from acgweb import app, db
import acgweb.const as CONST
from acgweb import config
from template_filter import *


import xlwt


def export_salary(rank_list,starttime,endtime):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(u'工资概要')

    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',num_format_str='#,##0.00')
    #style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

    if starttime and endtime:
        title = u"%s 至 %s 工资统计" % ( timeformat_filter( starttime,'%Y年%m月%d日'), timeformat_filter( int(endtime) - 24 * 3600, '%Y年%m月%d日') )
    elif starttime and not endtime:
        title = u"%s 之后 工资统计" % timeformat_filter( starttime,'%Y年%m月%d日')
    elif not starttime and endtime:
        title = u"%s 之前 工资统计" % timeformat_filter( int(endtime) - 24 * 3600, '%Y年%m月%d日')
    else:
        title = u"全部工资统计"

    title += " 统计时间 %s" % timeformat_filter( int(time.time()) ,'%Y-%m-%d %H:%M:%S')

    ws.merge(0, 0, 0, 7)
    ws.write(0, 0, title, style0)
    ws.write(1, 0, u"学号")
    ws.write(1, 1, u"姓名")
    ws.write(1, 2, u"总工时")
    ws.write(1, 3, u"上班工资")
    ws.write(1, 4, u"奖励工资")
    ws.write(1, 5, u"总计工资")
    ws.write(1, 6, u"银行卡号")
    ws.write(1, 7, u"备注")

    ws.col(0).set_width(256*12)
    ws.col(1).set_width(256*7)
    ws.col(2).set_width(256*6)
    ws.col(3).set_width(256*8)
    ws.col(4).set_width(256*8)
    ws.col(5).set_width(256*8)
    ws.col(6).set_width(256*26)
    ws.col(7).set_width(256*20)

    i=2
    for member in rank_list:
        extra_salary = 0
        ### TODO monitor salarsy top3 salary etc...
        ws.write(i, 0, member['uid'])
        ws.write(i, 1, member['name'])
        ws.write(i, 2, member['time'] / 3600)
        ws.write(i, 3, CONST.salaperhour * member['time'] / 3600)
        ws.write(i, 4, extra_salary)
        ws.write(i, 5, xlwt.Formula( "D%d+E%d" % (i+1,i+1) ))
        ws.write(i, 6, member['credit_card'])
        i += 1

    ws = wb.add_sheet(u'工资明细')

    ws.merge(0, 0, 0, 4)
    ws.write(0, 0, title, style0)
    ws.write(1, 0, u"姓名")
    ws.write(1, 1, u"时间")
    ws.write(1, 2, u"地点")
    ws.write(1, 3, u"活动")
    ws.write(1, 4, u"工时")

    ws.col(0).set_width(256*7)
    ws.col(1).set_width(256*16)
    ws.col(2).set_width(256*5)
    ws.col(3).set_width(256*60)
    ws.col(4).set_width(256*5)


    i=2
    for member in rank_list:
       for duty in member['salalist']:
            ws.write(i, 0, member['name'])
            ws.write(i, 1, timeformat_filter(duty['start_time'],'%Y-%m-%d %H:%M'))
            ws.write(i, 2, venuename_filter(duty['venue']))
            ws.write(i, 3, duty['title'])
            ws.write(i, 4, duty['work_last_time'] / 3600 )
            i += 1
    return wb
