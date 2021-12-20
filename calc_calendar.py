# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import os


def make_date_csv():
    # 生成日历文件
    if os.path.exists("work_day.csv"):
        return
    date_list = [[], [], []]
    week = 5
    for year_num in range(2000, 2051):
        for month_num in range(1, 13):
            if month_num in {1, 3, 5, 7, 8, 10, 12}:
                day_num = 31
            elif month_num in {4, 6, 9, 11}:
                day_num = 30
            else:
                if year_num % 100 == 0:
                    if year_num % 400 == 0:
                        day_num = 29
                    else:
                        day_num = 28
                else:
                    if year_num % 4 == 0:
                        day_num = 29
                    else:
                        day_num = 28
            for day in range(1, day_num + 1):
                week = week % 7
                work = 0 if week > 4 else 1
                date_list[0].append(year_num*10000+month_num*100+day)
                date_list[1].append(week + 1)
                date_list[2].append(work)
                week += 1
    date_dict = {"date_num": date_list[0], "week": date_list[1], "work": date_list[2]}
    p1 = pd.DataFrame.from_dict(date_dict)
    p1 = p1.set_index("date_num")
    p1.to_csv("work_day.csv")


def get_workday(dt=None, days=0, months=0, years=0, day_flag=2, work_flag=1):
    '''
    计算和传入日期间隔  days   个工作日的日期,  传入的日期不参与计数
    :param dt: 传入一个时间类型的参数
    :param days: 计算需要几个工作日
    :param months: 计算需要间隔的月份
    :param years: 计算需要间隔的年份
    :param day_flag: 返回时间时分秒格式  0:0点   1:原时间   2:24点
    :param work_flag: 返回日期类型  0:节假日   1:工作日   2:自然日
    :return:
    '''
    if not dt:
        return None

    day_df = pd.read_csv("work_day.csv")

    over_month = False
    dt_num = dt.year * 10000 + dt.month * 100 + dt.day

    months = int(months)
    years = int(years)
    days = int(days)
    day_flag = int(day_flag)
    work_flag = int(work_flag)
    # 计算时间格式
    if day_flag == 0:
        hour, minute, second = 0, 0, 0
    elif day_flag == 1:
        hour, minute, second = dt.hour, dt.minute, dt.second
    else:
        hour, minute, second = 23, 59, 59
    # 计算跨月跨年
    if months != 0:
        tmp_months = dt.month + months
        over_month = True
        if tmp_months == 0:
            months = 12 - dt.month
            years -= 1
        elif tmp_months // 12 != 0 and tmp_months % 12 != 0:
            months = tmp_months % 12 - dt.month
            years += (tmp_months // 12)
        elif tmp_months // 12 != 0 and tmp_months % 12 == 0:
            months = 12 - dt.month
            years += (tmp_months // 12 - 1)
        dt_num = dt_num + months * 100
    if years != 0:
        over_month = True
        dt_num = dt_num + years * 10000

    # 计算大于28号的数据,每个月的最后一天不一定一致
    if over_month and dt.day > 28:
        dt_day = day_df[day_df['date_num'] == dt_num].head(1)
        if dt_day.empty:
            dt_num = day_df[day_df['date_num'] <= dt_num].head(1)['date_num']

    # 计算时间前后
    if days > 0:
        search_condition = day_df['date_num'] > dt_num
    elif days < 0:
        days = abs(days)
        search_condition = day_df['date_num'] < dt_num
    else:
        days = 1
        search_condition = day_df['date_num'] >= dt_num

    # 返回时间类型
    if work_flag == 0:
        search_condition = search_condition & (day_df['work'] == 0)
    elif work_flag == 1:
        search_condition = search_condition & (day_df['work'] == 1)
    if days < 0:
        ret_ymd = day_df[search_condition].tail(days).head(1)['date_num'].values[0]
    else:
        ret_ymd = day_df[search_condition].head(days).tail(1)['date_num'].values[0]
    ret = datetime.datetime(year=ret_ymd // 10000,
                            month=ret_ymd % 10000 // 100,
                            day=ret_ymd % 10000 % 100, hour=hour, minute=minute, second=second)
    return ret


make_date_csv()
date_now = datetime.datetime.now()
b = get_workday(date_now, days=1, months=1, years=1, work_flag=1)
print(b)
