# coding: utf-8

salaperhour = 11
max_time = 2147483647L

article_category = [
    #{'id':0,'name':'未知'},
    {'id': 1, 'name': '新闻通知'},
    {'id': 2, 'name': '经验分享'},
    {'id': 3, 'name': '会议记录'},
    {'id': 4, 'name': '规章制度'},
    {'id': 5, 'name': '技术文档'},
    {'id': 6, 'name': '其他文章'},
]

categorysellect = [(i['id'], i['name']) for i in article_category]
categorysellect.insert(0, (0, '未分类'))

categoryname = [i['name'] for i in article_category]
categoryname.insert(0, '未分类')

#pagination
article_per_page = 20
activity_per_page = 15
member_per_page = 20
duty_per_page = 10
dutylist_per_page = 20
rank_index_page = 5
duty_index_page = 3
message_per_page = 20
schedule_per_page = 20
activity_index_num = 6
article_index_num = 5

sexname = ['未知', '男', '女']
mobiletypename = ['未知', '移动', '联通', '电信', '其他']

membertype = ['unknown', 'normal', 'busy', 'intern', 'history', 'eliminated', 'other']
membertypename = ['未知', '正常', '休班', '实习', '历史', '淘汰', '其他']

classtypename = ['未知', '必修课', '选修课', '其他']
messagetypename = {0: '未知', 1: '广播', 2: '排班', 9: '用户'}
dutylogtypename = {'equip': '设备记录', 'disc': '报告纪律班长', 'tech': '报告技术班长', 'arra': '报告排班班长', 'prev': '通知前音控员', 'next': '通知后音控员'}

#venueid = [ '', '305', '513', 'd4' ]

venue = ['unknown', '305', '513', 'd4']
venuename = ['未知', '305', '513', '东四']
venuecolor = ['inverse', 'warning', 'important', 'info']

activitytypename = ['未知', '招聘', '晚会', '会议' ,'其他']
activitytypecolor = ['inverse', 'info', 'important', 'warning', 'inverse']

ACTIVITY_UNKNOWN = 0
ACTIVITY_SCHEDULING = 1
ACTIVITY_ONGOING = 2
ACTIVITY_ENDED = 3
ACTIVITY_CANCELED = 4

activitystatusname = ['未知', '排班中', '正在进行', '已结束', '已取消']
activitystatuscolor = ['inverse', 'info', 'success', 'default', 'warning']

DUTY_UNKNOWN = 0
DUTY_APPLY_ING = 1
DUTY_APPLY_CONFIRM = 2
DUTY_APPLY_REJECTED = 3
DUTY_ARRANGE_CONFIRM = 4
DUTY_ARRANGE_REJECTED = 5
DUTY_BEFORE_START = 6
DUTY_REPLACE_ING = 7
DUTY_REPLACE_ED = 8
DUTY_ACTIVITY_CANCELED = 9
DUTY_ACTIVITY_ONGOING = 10
DUTY_ACTIVITY_ENDED = 11
DUTY_ARRANGE_CANCEL = 12
DUTY_APPLY_CANCEL = 13

dutystatusname = ['未知', '等待班长批准申请', '等待音控员确认', '班长拒绝了你的申请', '排班等待确认', '音控员拒绝了排班', '等待活动开始', '等待其他音控员代班', '其他音控员代班成功', '活动取消', '活动进行中', '活动结束', '排班取消', '已撤销值班申请']
dutystatuscolor = ['inverse', 'warning', 'important', 'default', 'important', 'default', 'success', 'warning', 'default', 'default', 'success', 'default', 'default', 'default']

dutyoperationname = {
    'activity_appoint': {'color': 'success', 'title': '安排值班', 'loading': '正在排班'},
    'apply_duty': {'color': 'success', 'title': '申请值班', 'content': '仅能申请一周内的活动，申请值班成功后不可以拒绝', 'loading': '正在申请', 'require_input': True},
    'approve_apply': {'color': 'success', 'title': '批准值班', 'loading': '正在处理'},
    'decline_apply': {'color': 'danger', 'title': '拒绝值班', 'loading': '正在处理'},
    'confirm_apply': {'color': 'success', 'title': '确认值班', 'content': '核对日期时间无误后确认值班', 'loading': '正在处理'},
    'accept_duty': {'color': 'success', 'title': '接受值班', 'loading': '正在处理'},
    #'decline_duty': {'color': 'danger', 'title': '不能值班', 'content': '填写你不能值班的原因', 'loading': '正在处理', 'require_input': True},
    'decline_duty': {'color': 'danger', 'title': '不能值班', 'content': '请主动联系排班班长说明原因，排班班长会取消排班。', 'disable': True},
    'request_cover': {'color': 'danger', 'title': '请求代班', 'content': '填写需要代班的原因', 'loading': '正在处理', 'require_input': True},
    'cancel_cover': {'color': 'danger', 'title': '取消带班', 'loading': '正在处理'},
    'cover_duty': {'color': 'success', 'title': '代他值班', 'loading': '正在处理'},
    'term_activity': {'color': 'danger', 'title': '结束活动', 'loading': '正在处理'},
    'cancel_task': {'color': 'danger',  'title': '取消任务', 'content': '确定要取消排班吗？', 'loading': '正在处理'},
    'cancel_apply': {'color': 'danger',  'title': '撤销申请', 'content': '确定要撤销值班申请吗？', 'loading': '正在取消'},
}


'''
1 正在申请值班 音控员已申请，等待班长批准
2 班长批准值班 班长已批准，等待音控员最终确认
3 班长拒绝值班 班长拒绝了值班申请
4 排班等待确认 班长排了班，等待音控员确认
5 排班拒绝值班 音控员有事情，不能值班
6 等待活动开始 接受值班任务
7 申请换班中   等待其他音控员换班
8 换班成功     换班成功
9 活动取消     主办方取消活动
10 活动进行中
11 活动结束
12 任务取消 班长取消了值班任务
13 取消申请值班 音控员取消了值班任务
'''


duty_status_operation_selfuser_mapper = {0: ['apply_duty'], 1: ['cancel_apply'], 2: ['confirm_apply'], 3: [], 4: ['accept_duty', 'decline_duty'], 5: [], 6: ['request_cover'], 7: ['cancel_cover'], 8: [], 9: ['term_activity'], 10: [], 11: [], 12: [], 13: []}

duty_status_operation_otheruser_mapper = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: ['cover_duty'], 8: [], 9: [], 10: [], 11: [], 12: [], 13: []}

duty_status_operation_monitor_mapper = {0: ['arrange_duty'], 1: ['approve_apply', 'decline_apply'], 2: [], 3: [], 4: ['cancel_task'], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: []}

duty_status_operation_next = {'apply_duty': 1, 'confirm_apply': 6, 'accept_duty': 6, 'decline_duty': 5, 'request_cover': 7, 'cancel_cover': 6, 'term_activity': 11, 'cover_duty': 8, 'approve_apply': 2, 'decline_apply': 3, 'cancel_task': 12, 'cancel_apply': 13}

dutylogtypename = {'equip': '设备记录', 'disc': '报告纪律班长', 'tech': '报告技术班长', 'arra': '报告排班班长', 'prev': '通知前音控员', 'next': '通知后音控员', 'host': '活动方记录', 'blame': '抱怨吐槽'}
