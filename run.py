import MailManager
import time
import gc
from selenium import webdriver
import json

print("该程序每两分钟执行一次检测是否有新的邮件，并将邮件解析，验证。通过后添加到json文件中！")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

email_count_path = 'email_index.json'
femail_count = open(email_count_path)
email_count_js = json.loads(femail_count.read())
last_email_count = email_count_js["index"]
while True:
    print("====================开始位置====================")
    now_time = time.strftime("%H:%M:%S", time.localtime())
    print("当前时间 ： " + now_time)
    now_time = int(now_time.replace(":", ''))
    if 90000 <= now_time <= 210000:
        a = MailManager.run(last_email_count=last_email_count, driver=driver)
        last_email_count = a
        s = {"index": last_email_count}
        json.dump(s, open(email_count_path, 'w'))
        print("下次将从第 " + str(last_email_count) + "  封邮件开始接收")
        print("====================结束位置====================")
        time.sleep(600)
    else:
        a = MailManager.run(last_email_count=last_email_count, driver=driver)
        time.sleep(3600)
    del a
    gc.collect()
