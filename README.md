
# Wireguard LDAP or Active Directory

С момощью этого сервиса можно реализовать выдачу VPN через LDAP или Active Directory


## Installation

Считаем, что wireguard у Вас уже установлен, если нет, то [устанавливаем](https://www.wireguard.com/install/).

Для начала скопируем себе репозиторий и перейдем в папку:

```
cd /opt/
git@github.com:viktor-gorinskiy/wireguard-ldap.git
cd wireguard-ldap
```
Следующие команды нужны для virtualenv (venv)
```
python3 -m venv .env
source .env/bin/activate
```
### Теперь установим нужные зависимости:

#### python-ldap
У меня всё работает на CentOS 7 и для установки python-ldap требуются следующие пакеты:
```
yum groupinstall "Development tools"
yum install openldap-devel python-devel
```
Теперь можно ставить python-ldap

```
pip install python-ldap
```

#### pillow

Для pillow так-же надо установить зависимости:

```
yum install libjpeg-turbo-devel
yum install zlib-devel
```
Ставим pillow
```
pip install pillow
```
#### qrcode
```
pip install qrcode
```

#### jinja2
Для работы удобства работы с шаблоном для email я использовал jinja2
```
pip install jinja2
```

Для запуска я использую две задачи в Cron, первая раз в 5 минут запускает сервис.

Вторая используется как напоминалка и "спамит" каждый понедельник в 15:00.

Это не будет работать в venv.
```
*/5 * * * * cd /opt/wireguard-ldap/ && /usr/bin/python3 /opt/wireguard-ldap/main.py
0 15 * * Mon cd /opt/wireguard-ldap/ && /usr/bin/python3 /opt/wireguard-ldap/email_send.py
```