"""
此程序主要负责接收邮件，并将新用户添加到数据列表中
"""

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import base64
import poplib
from email.parser import Parser
from email.utils import parseaddr
from email.header import decode_header
import time
import json
import gc


def send_MAIL(title, send_msg, receiver):
    """
    :param send_msg: 所要发送的内容
    :param title: 发送的标题
    :param receiver: 收件人邮箱
    :return:
    """

    # 发件人地址
    send_address = ""  # 你的邮箱
    send_pwd = "" # 你邮箱的密码，不是真正的密码，是原邮箱生成的POP3内个

    # 服务器
    smtp_server = 'smtp.qq.com'     # 根据你的邮箱服务器进行更改

    try:
        # 所发送内容
        msg = MIMEText(send_msg, 'plain', 'utf-8')

        # 邮箱头信息
        msg['From'] = Header(send_address)
        msg['To'] = Header(receiver)
        msg['Subject'] = Header(title)

        _server = smtplib.SMTP_SSL(host=smtp_server)
        _server.connect(smtp_server, 465)
        _server.login(send_address, password=send_pwd)
        _server.sendmail(send_address, receiver, msg.as_string())
    except:
        pass



# 链接到邮件
def get_mail():
# region 这里保存的是密码
    # 发件人地址
    send_address = ""  # 你的邮箱
    send_pwd = "" # 你邮箱的密码，不是真正的密码，是原邮箱生成的POP3内个
# endregion

    # 邮箱服务器地址
    pop3_server = 'pop.qq.com'      # 根据服务器进行更改

    # 链接邮箱服务器
    server = poplib.POP3(pop3_server)
    # server.set_debuglevel(1)

    # 检测是否连接到了服务器
    # print(server.getwelcome().decode('utf-8'))

    # 进行登录
    server.user(send_address)
    server.pass_(send_pwd)
    return server


# 获取邮件总数目
def get_mail_count(server):
    email_count, email_size = server.stat()
    print("消息数目：{0}, 消息大小:{1}".format(email_count, email_size))
    return email_count

# 获取邮件内容
def get_mail_info(server, email_count, last_email_count):
    all_info = []
    print("本次将从第： " + str(last_email_count) + " 封邮件开始结接收")
    for i in range(last_email_count, email_count + 1):
        rsp, msglines, msgsiz = server.retr(i)
        msg_content = b'\r\n'.join(msglines).decode('gbk')
        msg = Parser().parsestr(text=msg_content)
        subject = parser_subject(msg)
        sender_address = parser_sender(msg)
        content = parser_content(msg)
        all_info.append([subject, sender_address, content])
    server.close()
    return all_info, email_count+1



# 解析邮件主题
def parser_subject(msg):
    subject = msg['Subject']
    value, charset_subject = decode_header(subject)[0]
    if charset_subject:
        value = value.decode(charset_subject)
    print("邮件主题为：" + str(value))
    return value

# 解析发件人邮箱和发件人姓名
def parser_sender(msg):
    hdr, addr = parseaddr(msg['From'])
    name, charset_address = decode_header(hdr)[0]
    if charset_address:
        sender_name = name.decode(charset_address)
    print("发件人邮件地址为：" + str(addr))
    return addr

# 解析邮件内容
def parser_content(msg):
    content = msg.get_payload()

    # 获取邮件内容编码格式
    content_charset = content[0].get_content_charset()
    text = content[0].as_string().split('base64')[-1]
    text_content = base64.b64decode(text).decode(content_charset)
    print("文本信息为：" + str(text_content))
    return text_content
# 检查用户账户密码是否正确
def check(driver, usr_account, usr_pwd):
    url = "http://xscfw.hebust.edu.cn/survey/login"
    driver.get(url)
    time.sleep(2)
    try:
        driver.find_element_by_name("user").send_keys(usr_account)
        driver.find_element_by_name("pwd").send_keys(usr_pwd)
        driver.find_element_by_id("login").click()
    except:
        return False
    time.sleep(2)
    try:
        driver.find_element_by_xpath("/html/body/header/div/span")
        return True
    except:
        return False


# 解析用户信息并验证保存
def parser_usrInfo(driver, info):
    usr_email_address = None
    usr_name = None
    usr_account = None
    usr_pwd = None
    if info[0] == "体温填报":
        usr_info = None
        usr_email_address = info[1]
        try:
            usr_info = info[2].replace(',', " ")
            usr_info = info[2].replace("，", " ")
            usr_info = usr_info.split()
            print("解析内容为：" + usr_info)
        except:
            pass
        try:
            usr_name = usr_info[0]
            usr_account = usr_info[1]
            usr_pwd = usr_info[2]
        except:
            send_MAIL(title="验证未通过", send_msg="亲爱的"+usr_name+"同学：\n"+"    对不起，请您正确按照格式发送邮件，否则系统将无法为您保存！", receiver=usr_email_address)
            print("系统未成功为" + usr_name + "同学保存信息！")
        iskey = check(driver, usr_account=usr_account, usr_pwd=usr_pwd)
        if iskey:
            fpath = open('Username_Password.json', encoding='utf-8')
            temp_all_usrData = json.loads(fpath.read())
            temp_usr = {str(usr_account): {"name": usr_name, "username": usr_account, "password": usr_pwd, "mailAddress": usr_email_address}}
            temp_all_usrData.update(temp_usr)
            json.dump(temp_all_usrData, open('Username_Password.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
            # 给用户发邮件，提示其信息已经加入到数据中心
            send_MAIL(title="验证已通过", send_msg="亲爱的"+usr_name+"同学：\n"+"    系统已经成功验证并保存了您的信息", receiver=usr_email_address)
            print("系统已成功为" + usr_name + "同学保存信息！")
        else:
            # 如果验证不通过，提示用户验证未通过
            send_MAIL(title="验证未通过", send_msg="亲爱的"+usr_name+"同学：\n"+"    对不起，您输入的信息有误，请正确填写学号及密码！", receiver=usr_email_address)
            print("系统未成功为" + usr_name + "同学保存信息！")


# 执行程序
def run(last_email_count, driver):
    driver = driver

    all_info = None

    server = get_mail()
    email_count = get_mail_count(server)
    all_info, last_email_count = get_mail_info(server, email_count, last_email_count)
    try:
        server.quit()
    except:
        pass
    for info in all_info:
        parser_usrInfo(driver, info=info)
        time.sleep(5)
    time.sleep(10)
    del server
    gc.collect()
    return email_count+1

