from Telnet import Telnet
import re
import time
from netaddr import *


class Fiberhome:

    def __init__(self, host, username, password):
        self.telnet = Telnet(host, username, password)
        self.telnet.send_command("ENABLE")
        self.telnet.send_command(password)
        self.telnet.recv_all()

    def get_id(self, id=1):
        if not id in self.onu_pon_list:
            return id
        return self.get_id(id + 1)

    def get_unauth_onus(self):
        self.telnet.send_command("cd gpononu")
        self.telnet.send_command("show unauth list")
        self.telnet.send_command("cd .")
        unaths = {}
        finded = re.findall(r'(.*?FHTT*...+)', self.telnet.recv_all())
        for onu in finded:
            onu = onu.replace(' ', '').split(',')
            unaths[onu[0]] = {
                'serial': onu[1],
                'slot': onu[5],
                'pon': onu[6]
            }
        return unaths

    def get_onu_mac(self, slot, pon, id, phyid, timeout = 4):
        time.sleep(2)
        self.telnet.send_command("cd gpononu")
        self.telnet.send_command("show mac_list slot {} link {} onu {} port 1".format(slot, pon, id))
        mac = None
        ct = 0
        while not mac:
            retorno = self.telnet.recv_all()
            line = re.search(r'(.*' + self.cut_mac(phyid) + '.*)', retorno)
            if line:
                mac = re.search(r'([0-9A-F]{2}(?::[0-9A-F]{2}){5})', line.group()).group()
            else:
                if ct == timeout:
                    break
                time.sleep(1)
        return mac

    def cut_mac(self, macr):
        mac = ''
        i = 0
        for letra in macr:
            mac += letra
            i += 1
            if i == 2 and len(mac) < 17:
                mac += ":"
                i = 0
        return mac[8:-1].upper()

    def convert_pppoe_mac(self, mac_address):
        mac = EUI(mac_address)
        mac2 = EUI('00:00:00:00:00:03')
        return str(EUI(int(hex(mac), 16) + int(hex(mac2), 16))).replace('-', ':')

    def authorize_onu(self, phy_addr):
        self.telnet.send_command("cd gpononu")
        self.telnet.send_command(
            "set whitelist phy_addr address {} password null action add slot null link null onu null type null".format(phy_addr))

        if self.telnet.check_response("set onu whitelist ok"):
            self.telnet.send_command("cd .")
            time.sleep(10)
            return True
        else:
            self.telnet.send_command("cd .")
            time.sleep(10)
            return False

    def unauthorize_onu(self, phy_addr):
        self.telnet.send_command("cd gpononu")
        self.telnet.send_command(
            "set whitelist phy_addr address {} password null action delete slot null link null onu null type null".format(phy_addr))

        if self.telnet.check_response("set onu whitelist ok"):
            self.telnet.send_command("cd .")
            time.sleep(5)
            return True
        else:
            self.telnet.send_command("cd .")
            time.sleep(5)
            return False

    def get_pon_free_id(self, slot, pon):
        self.onu_pon_list = []
        self.telnet.send_command("cd gpononu")
        self.telnet.send_command("show onu_ver slot {} link {}".format(slot, pon))
        self.telnet.send_command("cd .")
        onuspon = re.findall(r'(.*?RP[0-9]...+?)', self.telnet.recv_all())
        for onupon in onuspon:
            onupon = re.search("\d+", onupon)
            self.onu_pon_list.append(int(onupon.group()))
        return self.get_id()

    def set_pppoe_onu(self, slot, pon, id, login, passwd, vlan):
        print("{} {} {}".format(slot, pon, id))
        self.telnet.send_command("cd gpononu")
        self.telnet.send_command("cd epononu")
        self.telnet.send_command("cd qinq")
        self.telnet.send_command('set wancfg slot {} {} {} index 1 mode internet type route {} 0 nat enable qos '
                                 'disable dsp pppoe proxy disable {} {} {} auto'.format(slot, pon, id, vlan, login,
                                                                                        passwd, login))
        self.telnet.send_command('set wanbind slot {} {} {} index 1 entries 1 fe1'.format(slot, pon, id, vlan, login, passwd, login))
        self.telnet.send_command('apply wancfg slot {} {} {} '.format(slot, pon, id))
        self.telnet.send_command('cd .')
        self.telnet.send_command('cd .')

    def save(self):
        self.telnet.send_command("save")

    def make_ftp_backup(self, server_ip, username, password, filename):
        self.telnet.send_command("upload ftp config {} {} {} {}".format(server_ip, username, password, filename))
