import time
import vk_requests

import pandas as pd
from openpyxl import load_workbook
from bs4 import BeautifulSoup
import requests

#time_ = 1567346400


#cur_home_work = open('homework.txt', 'r').read()




api=vk_requests.create_api(service_token='5e1d45161897de654370538732a885a2a88d98f7e4960f9ef5e94c5e5a32c1b48ac099b431388ec231429',
                                                   api_version='5.44');


def get_xlsx_table():
    host = 'http://www.masu.edu.ru'
    r = requests.get('http://www.masu.edu.ru/student/timetable/fmen/')
    bs = BeautifulSoup(r.text)
    url_table = bs.find('table', {'class':"center-2 center-3"}).a.attrs['href']
    r = requests.get(host+url_table)
    
    if r.status_code == 200:
        with open('table.xlsx','wb') as f:
            f.write(r.content)
    else:
        print('Скачка не удалась')


def get_classes(classes_and_time, cur_day, cur_week):
    
    time_classes = classes_and_time.iloc[1+15*(-1+cur_day):15*cur_day, (cur_week-1)*2:(cur_week-1)*2+2].dropna().iloc[:, 0].values
    time_classes = [[ times for _ in range(1,2) ] for times in time_classes]
    classes = classes_and_time.iloc[1+15*(-1+cur_day):15*cur_day, cur_week*2-1].dropna().values

    for i, class_ in enumerate(classes[::2]):
        time_classes[i].append(class_)
    for i, class_ in enumerate(classes[1::2]):
        time_classes[i].append(class_)
    
    
    
    #for i in range(len(time_classes)): 
    #    time_classes[i].append([classes.pop(0), classes.pop(0)])
    
    
    
    ret = ''
    
    for class_ in time_classes:
        print(class_)
        ret += ' '.join(class_)
        ret += '\n'
    return ret
 



def get_day_week(time_ = 0):
    start_time = 1567260000#-86400
    if time_ == 0:
        cur_time = int(time.time())
    else:
        cur_time = time_
        
    day = (cur_time - start_time) // 86400
    return  int(day % 7), int(((day-1) // 7) + 1)



def get_classes_and_time():
    wb = load_workbook('table.xlsx')
    sheet = wb['1БПМИ-ПТ']
    df = pd.DataFrame(sheet.values)[9:]
    return df.iloc[:, 1:]






try:
    cur_info = open('cur_info.txt','r').read().strip()
    dw_last = eval(open('dw_last.txt','r').read().strip())
    status_change = 0
except Exception as err:
    print(err)
    cur_info = ''
    dw_last = (0,0)
    status_change = 1




#time_ = time.time()+86400
print('Запуск мэйн цикла')
while True:
    get_xlsx_table()
    classes_and_time = get_classes_and_time()
    day, week = get_day_week()
    info = get_classes(classes_and_time, day, week).strip()
    
    
    if dw_last != (day,week):
        print('Текущая дата не совпадает с новополученой ', \
              '\nСтарое значение ', str(dw_last),\
              '\nНовое значение ', str((day,week)))
        
        status_change = 1
        cur_info = info
        dw_last = (day,week)
        open('dw_last.txt','w').write(str(dw_last))
        if dw_last[0] == 0:
            print('Воскресенье')
            cur_info = 'Зaвтра выходной'
            

    else:
        if cur_info != info:
            print('Изминение в Расписании')
            status_change = 1
            cur_info = 'Расписание изминилось с\n'+cur_info+'\nна\n'+info
            

            
           

    if status_change == 1:
        print('Отравка актуального расписания')
        status_change = 0
        api.messages.send(group_id='186081577', peer_id='2000000004',message=cur_info)
        cur_info = info
        open('cur_info.txt','w').write(cur_info)

        #ФУнкция смены данных
    del info
    time.sleep(60*30)
    print('in process...')
