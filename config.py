
### ------------ LDAP ------------ ###

ldap = True                    #   Использовать лдап для поиска пользователей?
ldap_url = 'ldap://ldap.domain.com:389'
ldap_bind_user = 'admin_vpn'
ldap_bind_pass = 'up9oJoXerohtaishoroer2Ijeugir4'
ldap_basedn = 'dc=domain,dc=loc'
ldap_filter = '(&(objectclass=inetorgperson)(memberOf=cn=vpn-users,cn=groups,cn=accounts,dc=sfxdx,dc=lan))' # Freeipa
ldap_filter = '(&(objectCategory=person)(objectClass=user)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(memberOf=CN=vpn-users,OU=groups,OU=DOMAIN,DC=domain,DC=loc))'   # AD
ldap_attrlist = {
    'user_name': 'uid',
    'user_contact': 'mail'
    }


### ------------ Wiereguard ------ ###

create_server_config = True     # Создавть конфиг wireguard сервера, если его нет?
start_server = True
    ## ---- Patches ---- ##
patch_wireguard = '/etc/wireguard'
peer_folder_config = '/etc/wireguard/peers'
peers_file_name = '/etc/wireguard/peers.txt'

    ## ---- server ---- ##
server = 'wg-server_1'
server_port = '51810'
server_ip = '10.10.6.1/24'
DNS = '8.8.8.8'
peer_ip_mask = 32
AllowedIPs = '10.10.0.0/18, 192.168.0.0/16'
Endpoint = 'vpn.domain.com'
publicKey = 'add_in_wireguard_server'
# preshared_key = ''

### ------- Email ------ ###

send_email_message = True

    ## ---- smtp ---- ##
smtp_port = 465
smtp_server = "smtp.gmail.com"
smtp_login = "informer@domain.com"
smtp_password = "Einahmai0yahwpvm_h3eemooXohSi"

smtp_Subject = "VPN_Compani_wireguard"
smtp_sender_email = smtp_login
smtp_template_html = 'email.html'
jinja_templates_folder = 'templates'

    ## ---- body ---- ## 
android_logo = 'images/android.png'
ios_logo = 'images/apple.png'
windows_logo = 'images/windows.png'
macOS_logo = ios_logo

href_ios = "https://apps.apple.com/us/app/wireguard/id1441195209?ls=1"
href_android = "https://play.google.com/store/apps/details?id=com.wireguard.android"
href_macOS = "https://itunes.apple.com/us/app/wireguard/id1451685025?ls=1&mt=12"
href_windows = "https://download.wireguard.com/windows-client/"

how_to_src = 'https://t.me/joinchat/group_id'   # or support link


### ------- Other config ------- ###

update_status_in_file = True            #   Добавлять ли информацию о подключении в файл с пирами "peers_file_name"
gen_peer_config_and_qr_files = False    #   Создавать локально конфиги и QR коды?
