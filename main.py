from selenium import webdriver
from time import sleep
import time
import random
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import parser
import poplib



# 邮件发送
def send_MAIL(title, send_msg, receiver):
    """
    :param send_msg: 所要发送的内容
    :param title: 发送的标题
    :param receiver: 收件人
    :return:
    """
    # 发件人地址及密码
    send_address = ""  # 你的邮箱
    send_pwd = "" # 你邮箱的密码，不是真正的密码，是原邮箱生成的POP3内个

    # 服务器
    smtp_server = 'smtp.qq.com'

    try:
        # 所发送内容
        msg = MIMEText(send_msg, 'plain', 'utf-8')

        # 邮箱头信息
        msg['From'] = Header(send_address)
        msg['To'] = Header(receiver)
        msg['Subject'] = Header(title)

        server = smtplib.SMTP_SSL(host=smtp_server)
        server.connect(smtp_server, 465)
        server.login(send_address, password=send_pwd)
        server.sendmail(send_address, receiver, msg.as_string())
        server.quit()
    except:
        pass



# 填写脚本程序
def run_main(name, usrname, password, mail_address, achieve_count, correct_send_mail_count):
    """

    :param name: 填报人
    :param usrname: 填报人学号
    :param password: 密码
    :param mail_address: 填报人邮箱
    :return:
    """
    # 打开浏览器
    url = 'http://xscfw.hebust.edu.cn/survey/login'
    isRun = False

    try:
        driver.get(url)
        sleep(2)
        driver.find_element_by_name('user').send_keys(usrname)
        driver.find_element_by_name('pwd').send_keys(password)
        driver.find_element_by_id('login').click()
        sleep(2)
        try:
            driver.find_element_by_class_name("mdui-list-item-content").click()
        except:
            isRun = True
        temp = driver.find_elements_by_class_name("mdui-textfield-input")
        temp[0].clear()
        morning_temp = str(random.uniform(36.3, 36.7))[:4:]
        temp[0].send_keys(morning_temp)
        sleep(0.2)
        temp[1].clear()
        afternoon_temp = str(str(random.uniform(36.3, 36.7))[:4:])
        temp[1].send_keys(afternoon_temp)
        sleep(1)
        driver.find_element_by_id("save").click()
        achieve_count += 1
        send_msg = "亲爱的" + name + "同学:\n    瓜皮助手已经成功为您填报体温！\n    上午体温填报的内容为：" + morning_temp + "\n    午间体温填报内容为：" + afternoon_temp
        send_MAIL(title="体温填报成功", send_msg=send_msg, receiver=mail_address)
        correct_send_mail_count += 1
    except:
        sleep(5)
        send_MAIL(title="体温填报失败", send_msg="亲爱的"+ name +"同学:\n\t叭好意思~~今天拉跨了~还需您自己填报体温！", receiver=mail_address)
    return achieve_count, correct_send_mail_count, isRun


# 读取用户账户密码
def get_usr_info(filePath):
    usr_info = None
    try:
        f = open(filePath, encoding='utf-8')
        usr_info = json.loads(f.read())
    except:
       print("出现了错误")
       pass
    return usr_info


if __name__ == '__main__':
    print("该程序每两分钟执行一次，检测当前时间是否在体温填报范围时间内。\n若在体温填报时间内，则开始填报，否则pass")
    filePath = "Username_Password.json"
    isRun = True
    achieve_count = 0
    correct_send_mail_count = 0
    driver = None
    while True:
        print("====================开始执行====================")
        now_time = time.strftime("%H:%M:%S", time.localtime())
        now_time = int(now_time.replace(':', ''))
        if 113000 <= now_time <= 133000 and isRun:
            isRun = False
            usr_info = get_usr_info(filePath)
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            achieve_count = 0
            correct_send_mail_count = 0
            for key in usr_info.keys():
                try:
                    achieve_count, correct_send_mail_count, isRun = run_main(name=usr_info[key]["name"],
                                                                      usrname=usr_info[key]["username"],
                                                                      password=usr_info[key]["password"],
                                                                      mail_address=usr_info[key]["mailAddress"],
                                                                      achieve_count=achieve_count,
                                                                      correct_send_mail_count=correct_send_mail_count)
                    if isRun == True:
                        break
                except:
                    print("error")
                    pass
            try:
                driver.close()
            except:
                pass
            send_MAIL(title="完成人数/总人数 = " + str(achieve_count) + "/" + str(len(usr_info)),
                      send_msg="完成人数/总人数 = " + str(achieve_count) + "/" + str(len(usr_info)) + "\n" +
                               "正确发送邮件" + str(correct_send_mail_count) + "封",
                      receiver="your-email@foxmail.com")  # <-输入你的邮箱，相当于管理员，每天接收总的填报情况

        elif 10000 <= now_time <= 100000:
            isRun = True
            time.sleep(3600)
        now_time = time.strftime("%H:%M:%S", time.localtime())
        print("当前时间" + str(now_time))
        print("====================本次执行结束====================")
        sleep(60)

