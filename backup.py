#!/usr/bin/python3
from Fiberhome import Fiberhome
from datetime import date

if __name__ == '__main__':
    bkday = date.today().strftime('%d-%m-%Y')
    fiberhome = Fiberhome('IP_DA_OLT', 'USUARIO', 'SENHA')
    fiberhome.make_ftp_backup("IP_SERVIDOR_FTP", "USUARIO_FTP", "SENHA_FTP", "/DIR_FTP/ARQUIVO_NOME-{}.cfg".format(bkday))
