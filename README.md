
# Wireguard LDAP or Active Directory

С момощью этого сервиса можно реализовать выдачу VPN через LDAP или Active Directory


## Installation

Считаем, что wireguard у Вас уже установлен, если нет, то [устанавливаем](https://www.wireguard.com/install/).


```
cd /opt/
git clone https://github.com/viktor-gorinskiy/wireguard-ldap.git
cd wireguard-ldap
mv example.config.py config.py
vim config.py
```
Последняя команда откроет конфиг файл на редактирование в vim
 
<details><summary>Как выйти из vim без сохранения:</summary>
   Esc
   Esc
   Esc
   :
   !
   q
   Enter
</details>
<details><summary>Как сохранить и выйти из vim:</summary>
   Esc
   Esc
   Esc
   :
   w
   q
   Enter
</details><br>


Следующие команды нужны для virtualenv (venv)  

```
python3 -m venv .env
source .env/bin/activate
```
### Теперь установим нужные зависимости:

#### python-ldap
##### завистимости
Для CentOS 7:
```
yum groupinstall "Development tools"
yum install openldap-devel python-devel
```
Для Ubuntu:
```
sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
```
Теперь можно ставить python-ldap

```
pip install python-ldap
```

#### pillow

Зависимости для CentOS 7 :

```
yum install libjpeg-turbo-devel
yum install zlib-devel
```
Зависимости для Ubuntu:
```
sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y
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