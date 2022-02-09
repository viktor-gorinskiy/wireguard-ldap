import ldap
import subprocess
import ipaddress
import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os
import qrcode
import tempfile
from jinja2 import Environment, select_autoescape, FileSystemLoader


# pip install python-ldap
# pip install qrcode
# pip install pillow

server = config.server
file_name = config.peers_file_name
ldap_url = config.ldap_url
ldap_bind_user = config.ldap_bind_user
ldap_bind_pass = config.ldap_bind_pass
ldap_basedn = config.ldap_basedn
ldap_filter = config.ldap_filter
ldap_attrlist =  config.ldap_attrlist

# Ищет новый IP адрес сортируя имеющиеся, добавляет IP в промежутках
def new_ip():
    ips = wireguard(action='info',who='ips')
    ips_tmp = []
    for ip in ips:
        ips_tmp.append(ip)
        try:
            ipaddress.ip_address(ip)
        except Exception as error:
            ips_tmp.remove(ip)

    ips = ips_tmp
    ips = sorted([ipaddress.ip_address(addr) for addr in ips])
    tmp_ip = ips[0]
    for ip in ips:
        if ip == tmp_ip:
            tmp_ip+=1
        else:
            return tmp_ip
    return ip + 1

# Ищет IP адрес в файле по индефикатору пользователя
def get_ip_in_file(peer_pub_key):
    try:
        ip = find_in_file(peer_pub_key = peer_pub_key)['ip']
    except KeyError as error:
        # print('ERROR', error)
        return False
    return ip

# Функция использует две фукции для поиска ip, тоесть запрашивает в файле и если нет, то запрашивает новый
def get_ip(public_key):
    ip = get_ip_in_file(public_key)
    if not ip:
        ip = new_ip()
    return ip

##########################################################

# Функция запрашивает пользователей из LDAP
def get_users_ldap():
    ad = ldap.initialize(ldap_url)
    ad.set_option(ldap.OPT_REFERRALS, 0)
    ad.simple_bind_s(ldap_bind_user, ldap_bind_pass)


    basedn = ldap_basedn
    scope = ldap.SCOPE_SUBTREE

    filterexp = ldap_filter
    attrlist = list(config.ldap_attrlist.values())
    results = ad.search_s(basedn, scope, filterexp, attrlist)
    print(results)
    # import sys
    # sys.exit(0)


    users_ldap = {}
    for result in results:
        if result[0] != None:
            if len(result[1]) > 1:
                ldap_user_name_attr = result[1][config.ldap_attrlist['user_name']][0].decode('utf-8')
                contact = result[1][config.ldap_attrlist['user_contact']][0].decode('utf-8')

                users_ldap[ldap_user_name_attr] = {}
                users_ldap[ldap_user_name_attr]["contact"] = contact

    return users_ldap
    
# Читает из файла строки и переделывает возвращает словарь
def file_to_dict():
    types = ['peer_pub_key', 'peer_private_key', 'name', 'contact', 'mail_status', 'ip', 'endpoint', 'handshake' ]
    with open(file_name, 'r') as file_handler:
        dict_file = []
        for line in file_handler:
            line = ' '.join(line.split()).split(' ')
            dict_file.append(dict(zip(types, line)))
    return dict_file

#   Редактирует файл, удаляет, добавляет, изменяет
def edit_per_to_file(find_pole='', find_key='', replace_pole='', replace_key='', **kwargs ):

    data_peers = []
    data_dict = file_to_dict()
    with open(file_name, 'w') as file_handler:
        for user in data_dict:
            # print(user)
            if replace_pole != 'new':
                if find_key == user[find_pole]:
                    if 'endpoint' in kwargs:
                        user['endpoint'] = kwargs['endpoint']
                    if 'handshake' in kwargs:
                        user['handshake'] = kwargs['handshake']

                    if replace_pole == 'del':
                        user.clear()
                    user[replace_pole] =  replace_key
                data_peers.append(user)

        if replace_pole == 'new':
            user = {}
            keys = wireguard('keys')
            peer_private_key = keys[0]
            peer_pub_key = keys[1]
            user['peer_pub_key'] = peer_pub_key
            user['peer_private_key'] =  peer_private_key
            if 'name' in kwargs:
                user['name'] = kwargs['name']
            if 'contact' in kwargs:
                user['contact'] = kwargs['contact']
            if 'endpoint' in kwargs:
                user['endpoint'] = kwargs['endpoint']
            if 'handshake' in kwargs:
                user['handshake'] = kwargs['handshake']

            user['mail_status'] = 1
            # types = ['peer_pub_key', 'peer_private_key', 'name', 'contact', 'mail_status', 'ip', 'status']

            data_peers = data_dict
            data_peers.append(user)

        for data_peer in data_peers:
            string = ''
            for c in data_peer:
                iter = str(data_peer[c])
                # print(iter)
                len_just = 20

                if len(iter) == 44:
                    len_just = 48
                elif len(iter) >= 15 and len(iter) < 43:
                    len_just = 35
                elif len(iter) <= 1:
                    len_just = 5
                string = string + iter.ljust(len_just, ' ')
            string = string.rstrip()
            if string:      #    Не записывать строку в файл, если она пустая (после удаления файла.)
                file_handler.write(string + '\n')

#   Ищет в файле по полям из словаря и возвращает результат
def find_in_file(**kwargs):
    # print('kwargs', kwargs)
    if 'mail_status' in kwargs:
        pole = 'mail_status'
        find = kwargs['mail_status']
    if 'status' in kwargs:
        pole = 'status'
        find = kwargs['status']
    if 'ip' in kwargs:
        pole = 'ip'
        find = kwargs['ip']
    if 'peer_pub_key' in kwargs:
        pole = 'peer_pub_key'
        find = kwargs['peer_pub_key']
    if 'peer_private_key' in kwargs:
        pole = 'peer_private_key'
        find = kwargs['peer_private_key']
    if 'name' in kwargs:
        pole = 'name'
        find = kwargs['name']
    if 'contact' in kwargs:
        pole = 'contact'
        find = kwargs['contact']

    if not kwargs:
        return file_to_dict()

    data_dict = file_to_dict()
    for user in data_dict:
        if find == user[pole]:
            return user
    return False

# перед добавлением нового пользователя в файл проверят нет ли его в файле
def add_new_user_in_file(name, contact ):
    # print('name',name, 'contact', contact )
    peer = find_in_file(name = name)
    if not peer:
        edit_per_to_file(replace_pole='new', name=name, contact=contact)
        return True

def get_config(peer_private_key, peer_ip, peer_name):
    result_config =  (
        f'[Interface]\n'
        f'Address = {peer_ip}\n'
        f'PrivateKey =  {peer_private_key}\n'
        f'DNS =  {config.DNS}\n\n'
        f'[Peer]\n'
        f'PublicKey = {config.publicKey}\n'
        f'#PresharedKey =\n'
        f'AllowedIPs = {config.AllowedIPs}\n'
        f'Endpoint = {config.Endpoint}:{config.server_port}\n'
    )
    return result_config

#   Генерирует конфиг файл и QR код
def gen_peer_config(peer_private_key, peer_ip, peer_name):
    peer_ip = str(peer_ip) + '/' + str(config.peer_ip_mask)
    config_peer = get_config(peer_private_key, peer_ip, peer_name)

    f_peer_name = config.peer_folder_config + '/wg-' + peer_name + '.conf'
    try:
        with open(f_peer_name, 'w') as file_handler:
            file_handler.write(str(config_peer))
    except FileNotFoundError:
        os.mkdir(config.peer_folder_config)
        with open(f_peer_name, 'w') as file_handler:
            file_handler.write(str(config_peer))


    qr = qrcode.QRCode()
    qr.add_data(config_peer)
    qr.make()
    img = qr.make_image()
    qr_jpg = config.peer_folder_config + '/' + peer_name + '.jpg'
    rgb_im = img.convert('RGB')
    rgb_im.save(qr_jpg)


    # f_peer_qr = config.peer_folder_config + '/' + peer_name + '.png'
    # qr = pyqrcode.create(config_peer)
    # qr.png(f_peer_qr, scale=5)

#   Функция для работы с Wireguard, возвращает список пиров, добавляет и удаляет пиры, генерирует приватный и публичный ключи
def wireguard(action='', public_key='', ip='', who=''):
    if action == 'add':
        ip = str(ip) + '/' + str(config.peer_ip_mask)
        cmd = f"""wg set  '{server}' peer '{public_key}' allowed-ips '{ip}'"""
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True

    if action == 'keys':
        cmd = f"""wg genkey"""
        peer_private_key = \
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode(
            'utf-8').rstrip()
        cmd = f"""/bin/echo '{peer_private_key}' | wg pubkey"""
        peer_pub_key = \
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode(
            'utf-8').rstrip()
        return peer_private_key, peer_pub_key

    if action == 'del':
        cmd = f"""wg set {server} peer  {public_key} remove"""
        # print(cmd)
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # print(res.communicate()[0].decode('utf-8'))
        return True

    if action == 'info':
        ips = []
        peers = []
        cmd = f"""wg show '{server}' allowed-ips"""
        result_wg_info = \
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode(
            'utf-8').split('\n')
        for l in result_wg_info:
            if l:
                ips.append(l.split('\t')[1].split('/32')[0])
                peers.append(l.split('\t')[0])
        if who == 'ips':
            return ips
        if who == 'peers':
            return peers

    if action == 'status':
        cmd = f"""wg show '{server}'"""
        result_wg_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')
        peers_online = {}
        for peer in result_wg_info.split('\n\n'):
            peer_data = peer.split('\n')
            peer = ''
            endpoint = ''
            handshake = ''
            allowed_ips = ''
            for data in peer_data:
                peer_dict = {}
                if 'peer:' in data:
                    peer = data.split('peer: ')[1]
                if 'endpoint: ' in data:
                    endpoint = data.split('endpoint: ')[1].split(':')[0]
                if 'latest handshake: ' in data:
                    handshake = str(data.split('latest handshake: ')[1].split(':')[0].split('\n')).strip('[]').replace(' ', '_').replace('\'', '')
                    # print(handshake)
                if 'allowed ips:' in data:
                    allowed_ips  =  data.split('allowed ips: ')[1].split(':')[0]

                if peer:
                    peer_dict['endpoint'] = endpoint
                    peer_dict['handshake'] = handshake
                    peer_dict['allowed_ips'] = allowed_ips
                    peers_online[peer] = peer_dict
        if peers_online:
            return peers_online
    return False

#   Отправляет сообщение на почту
def send_email(peer_pub_key):
    peer_date = find_in_file(peer_pub_key=peer_pub_key)
    user_name = peer_date['name']
    peer_private_key = peer_date['peer_private_key']
    peer_ip = peer_date['ip']
    receiver_email = peer_date['contact']

    message = MIMEMultipart("alternative")
    message["Subject"] = config.smtp_Subject
    message["From"] = config.smtp_sender_email
    message["To"] = receiver_email


    loader = FileSystemLoader(config.jinja_templates_folder)
    autoescape=select_autoescape(['html', 'xml'])
    env = Environment(loader=loader, trim_blocks=True, autoescape=autoescape)

    # данные для шаблона
    content = {}

    android = {"href":config.href_android}
    macOS = {"href":config.href_macOS}
    ios = {"href":config.href_ios}
    windows = {"href":config.href_windows}

    content['links'] = {
        'android':android,
        'macOS':macOS,
        'ios':ios,
        'windows': windows
        }
    content['how_to_src'] = config.how_to_src
    content['user_name'] = user_name

    # загружаем шаблон 'mytemplate.html'
    tpl = env.get_template(config.smtp_template_html)
    # рендерим шаблон в переменную `result`
    html = tpl.render(content)

    part = MIMEText(html, "html")
    message.attach(part)

    with open(config.windows_logo, 'rb') as img:
      windows_logo_image = MIMEImage(img.read())
    windows_logo_image.add_header('Content-ID', '<windows_logo>')
    message.attach(windows_logo_image)

    with open(config.android_logo, 'rb') as img:
        android_logo_image = MIMEImage(img.read())
    android_logo_image.add_header('Content-ID', '<android_logo>')
    message.attach(android_logo_image)

    with open(config.macOS_logo, 'rb') as img:
      macOS_logo_image = MIMEImage(img.read())
    macOS_logo_image.add_header('Content-ID', '<macOS_logo>')
    message.attach(macOS_logo_image)

    with open(config.ios_logo, 'rb') as img:
      ios_logo_image = MIMEImage(img.read())
    ios_logo_image.add_header('Content-ID', '<ios_logo>')
    message.attach(ios_logo_image)


    config_name = 'wg-' + user_name + '.conf'       # Имя файла для названия в письме
    config_peer = get_config(peer_private_key, peer_ip, user_name)   #   Генерируем текст конфига
    conf = MIMEApplication(config_peer)
    conf.add_header('Content-Disposition', 'attachment', filename=config_name)
    message.attach(conf)


    qr = qrcode.QRCode()
    qr.add_data(config_peer)
    qr.make()
    img = qr.make_image()
    rgb_im = img.convert('RGB')


    with tempfile.TemporaryDirectory() as temp:
        qr_file_pach = temp + '/qr' + '.jpg'    #   Создаем ПУТЬ ДО ВРЕМЕННОГО ФАЙЛА ВО ВРЕМЕННОЙ ДИРЕКТОРИИ
        rgb_im.save(qr_file_pach)               #   Сохраняем файл QR
        # Прикрепляем файл как вложение:
        with open(qr_file_pach, 'rb') as img:
            qr_file = MIMEApplication(img.read())
        qr_file.add_header('Content-Disposition', 'attachment', filename='qr.jpg')
        message.attach(qr_file)

        # Прикрепляем файл как картинка в html:
        with open(qr_file_pach, 'rb') as img:
            qr_image_to_html = MIMEImage(img.read())
        qr_image_to_html.add_header('Content-ID', '<QR>')
        message.attach(qr_image_to_html)


    with smtplib.SMTP_SSL(config.smtp_server, config.smtp_port) as server:
       server.ehlo()
       server.login(config.smtp_login, config.smtp_password)
       server.sendmail(
           config.smtp_sender_email, receiver_email, message.as_string()
       )

# Добавляет в файл информацию о ip адресе с которого подключился пиир и о времени последнего подключения
def update_status():
    peers_status = wireguard(action='status')
    # print('peers_status', peers_status)
    if peers_status:
        for status in peers_status.items():
            peer = status[0]
            endpoint = status[1]['endpoint']
            handshake = status[1]['handshake']
            edit_per_to_file(find_pole='peer_pub_key', find_key=peer, endpoint=endpoint, handshake=handshake)
        return True
    return False


#
print(get_users_ldap())
#
# print(ldap.__version__)
# print(wireguard(action='status'))