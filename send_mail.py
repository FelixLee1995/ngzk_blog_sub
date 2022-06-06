from lib2to3.pytree import Base
import smtplib
from email.mime.text import MIMEText
from email.header import Header
try:
    import winsound
except BaseException as e:
    print("cant find winsound, assuming use in unix os...")
from my_config import g_config

class Mail:
    def __init__(self):
        # 第三方 SMTP 服务

        self.mail_host = "smtp.qq.com"  # 填写邮箱服务器:这个是qq邮箱服务器，直接使用smtp.qq.com
        self.mail_pass = g_config.get_config('auth_code', '123134')  # 填写在qq邮箱设置中获取的授权码
        self.sender = g_config.get_config('sender_mail_address', 'xxxxx@qq.com')  # 填写发件邮箱地址
        self.nickname = g_config.get_config('sender_nick_name', 'John Doe')
        self.receivers = g_config.get_config("receiver_mail_list", [])  # 填写收件人的邮箱，QQ邮箱或者其他邮箱，可多个，中间用,隔开
        self.if_play_sound = g_config.get_config("if_play_sound", 0)

        print(f"开始运行乃木坂blog更新提醒工具， 发件人邮箱【{self.sender}】, 订阅者列表为【{self.receivers}】")

    def send(self, title: str, context: str, type: str):
        content = context   #邮件内容
        message = None
        if type == 'html':
            message = MIMEText(content, 'html', 'utf-8')
        else:
            message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header(self.nickname, 'utf-8')  #邮件发送者姓名
        message['To'] = Header("blog更新订阅者", 'utf-8')    #邮件接收者姓名

        subject = title  #发送的主题
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP_SSL(self.mail_host, 465) #建立smtp连接，qq邮箱必须用ssl边接，因此边接465端口
            smtpObj.login(self.sender, self.mail_pass)  #登陆
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())  #发送
            smtpObj.quit()
            print('发送成功！！')
            if self.if_play_sound == 1:
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

        except smtplib.SMTPException as e:
            print('发送失败！！')
        except BaseException as e:
            print("failed to play sound")

g_mail = Mail()