# этот скрипт нужен, если Вы хотите переодически отправлять клиентам их конфиги, независимо от статуса отправки
import wg_lib as wg

for user in wg.find_in_file():

    peer_name = user['name']
    peer_mail = user['contact']

    wg.send_email(user['peer_pub_key'])
    print('Send email',peer_name, peer_mail)

