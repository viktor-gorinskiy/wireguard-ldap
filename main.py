import wg_lib as wg
import config
import os
import sys


if not os.path.exists(config.patch_wireguard):
    print('Main folder not found wireguard!')
    print('EXIT')
    sys.exit(1)


#   Если нет конфига Wireguard и включена опция его создания, то сделаем это:
if config.create_server_config:
    #   Создадим переменную для имени файла сервера Wireguard.
    wireguard_server_config = config.patch_wireguard + '/' + config.server + '.conf'
    if not os.path.exists(wireguard_server_config):
        with open(wireguard_server_config, 'w') as file_handler:
            server_keys=wg.wireguard(action='keys') # генерируем ключи для сервера Wireguard
            server_private_key = server_keys[0]     # Это у нас приватный ключ
            server_public_key = server_keys[1]      # Это публичный ключ, он так-же добавляется в конфиг, но он там не используется
                                                    # его необходимо добавить в конфиг этого серивиса т.е. config.py ==> publicKey
            wireguard_server_config_strings = (
                f'[Interface]\n'
                f'Address = {config.server_ip}\n'
                f'ListenPort = {config.server_port}\n'
                f'PrivateKey = {server_private_key}\n'
                f'#PublicKey = {server_public_key}\t copy to config.py\n'
                
            )
            file_handler.write(wireguard_server_config_strings)
            current_patch = os.path.dirname(os.path.realpath(__file__))
            msg = (
                f'\nPlease run the following command to add the server\'s public key to this service:\n'
                f'\tsed -i "s/add_in_wireguard_server/{server_public_key}/" {current_patch}/config.py\n'
                f'And run wireguard server:\n'
                f'\tsystemctl start wg-quick@{config.server}.service\n\n'
                )
            print(msg)
            sys.exit(0)


if not os.path.exists(config.peers_file_name):
    if not config.peers_file_name:
        print('The path for the file with the list of users is not defined')
        print('Edit the parameter:')
        print('peers_file_name = \'/etc/wireguard/peers.txt\'')
        sys.exit(1)
    print('Create!', config.peers_file_name)
    with open(config.peers_file_name, 'w') as file:
        print('Successfully')


if config.gen_peer_config_and_qr_files:     # Проверим включена ли опция создания файлов
    if not os.path.exists(config.peer_folder_config):   # Проверим есть ли такая папка
        print('The folder for saving configuration files and QR codes was not found')
        if config.peer_folder_config:
            print('Create!', config.peer_folder_config)
            os.mkdir(config.peer_folder_config)
        else:
            print('The option to create configuration files and QR codes is enabled, but the path to save them is not defined!')
            print('Edit the parameter:')
            print('peer_folder_config = \'/etc/wireguard/peers\'')
            sys.exit(1)

if config.ldap:
    users_ldap = wg.get_users_ldap()   # Получаем список пользователей из LDAP
    print('Получаем список пользователей из LDAP')
    for user in users_ldap:
        print('LDAP',user,users_ldap[user]['contact'])
        wg.add_new_user_in_file(user,users_ldap[user]['contact'])   # Добавляем пользователей в файл, функция проверяет нет ли аналогичных пользователей в файле


    # Теперь получим список имен пользователей из файла
    users_file = wg.find_in_file()
    for user in users_file:
        # print(user['name'])
        if user['name'] not in users_ldap:          # Если пользователя нет в LDAP, то удалим строчку из файла!
            print('NOT IN LDAP!!!',user)
            wg.edit_per_to_file(find_pole='name', find_key=user['name'], replace_pole='del')    # Само удаление из файла
#
#
peers_online = wg.wireguard(action='info', who='peers')

for user in wg.find_in_file():

    if user['peer_pub_key'] not in peers_online: #   Проверим не онлайн ли этот пир сейчас
        print('Not online', user['name'])

        peer_ip = wg.get_ip(user['peer_pub_key'])
        peer_private_key = user['peer_private_key']
        peer_name = user['name']
        peer_mail = user['contact']
        peer_status_mail = int(user['mail_status'])
        wg.edit_per_to_file(find_pole='peer_pub_key', find_key=user['peer_pub_key'], replace_pole='ip',
                            replace_key=peer_ip)        # Добавляем IP в файл

        wg.wireguard(action='add', public_key=user['peer_pub_key'], ip=peer_ip)     #   Добавляем пир в WG
        print('Add peer ', peer_name, peer_ip)

        if config.gen_peer_config_and_qr_files:
            wg.gen_peer_config(peer_private_key, peer_ip, peer_name)  #   Гернерируем кофигфайл
            print('Generate_file ',peer_name, peer_ip)
            print()

        if config.send_email_message:    # Отправлять сообщения на почту?
            if peer_status_mail:
                wg.send_email(user['peer_pub_key'])
                wg.edit_per_to_file(find_pole='peer_pub_key', find_key=user['peer_pub_key'], replace_pole='mail_status', replace_key=0)
                print('Send email',peer_name, peer_status_mail)
    print()
if config.update_status_in_file:   # добавлять информацию о пире в файл после установления соединению
    wg.update_status()  #Обновим статус пиров в файле
