import subprocess
import ipaddress

class wireguard(object):
    """wireguard"""
 
    def __init__(self, server='', peer_ip_mask=32, dns=False, preshared_key=False, AllowedIPs='0.0.0.0', Endpoint='127.0.0.1', server_port=51820, start_ip='127.0.0.1'):
        """wireguard"""
        self.server = server
        self.peer_ip_mask = peer_ip_mask
        self.dns = dns
        self.preshared_key = preshared_key
        self.AllowedIPs = AllowedIPs
        self.Endpoint = Endpoint
        self.server_port = server_port
        self.start_ip = start_ip


    def add_peer(self, public_key):
        ip = str(ip) + '/' + str(sel.peer_ip_mask)
        cmd = f"""wg set  '{self.server}' peer '{public_key}' allowed-ips '{ip}'"""
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True

    def keys(self):
        cmd = f"""wg genkey"""
        peer_private_key = \
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8').rstrip()
        cmd = f"""/bin/echo '{peer_private_key}' | wg pubkey"""
        peer_pub_key = \
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8').rstrip()
        return peer_private_key, peer_pub_key

    def del_perer(self, public_key):
        cmd = f"""wg set {self.server} peer  {public_key} remove"""
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True

    def info(self):
        ips = []
        peers = []
        cmd = f"""wg show '{self.server}' allowed-ips"""
        result_wg_info = \
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8').split('\n')
        for ips_peers in result_wg_info:
            if ips_peers:
                ips.append(ips_peers.split('\t')[1].split(self.peer_ip_mask)[0])
                peers.append(ips_peers.split('\t')[0])

        return {'peers': peers, 'ips':ips}
    
    def get_server_publicKey(self):
        cmd = f"""wg show '{self.server}'""" + "| awk '/public key:/{print $3}'"
        result_get_server_publicKey = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8').split('\n')[0]
        return result_get_server_publicKey

    def status(self):
        cmd = f"""wg show '{self.server}'"""
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

    def new_ip(self):
        ips = self.info()['ips']
        if not ips:
            ips = []
            ips.append(self.start_ip)

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

    def get_config(self, peer_private_key, peer_ip, peer_name):
        publicKey = self.get_server_publicKey()
        dns = preshared_key = ''
        if self.dns:
            dns = f'DNS =  {self.dns}\n'
        if self.preshared_key:
            preshared_key = f'PresharedKey = {self.preshared_key}\n'

        result_config =  (
            f'[Interface]\n'
            f'Address = {peer_ip}\n'
            f'{dns}'
            f'PrivateKey =  {peer_private_key}\n\n'
            f'[Peer]\n'
            f'PublicKey = {publicKey}\n'
            f'{preshared_key}'
            f'AllowedIPs = {self.AllowedIPs}\n'
            f'Endpoint = {self.Endpoint}:{self.server_port}\n'
        )
        return result_config
