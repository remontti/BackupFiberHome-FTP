# Backup Fiberhome via FTP / SSH

Estre script (python3) acessa a OLT por SSH e executa o comando de envio do backup para um servidor FTP.

Edite o arquivo <b>backup.py</b> e altere os valores em negrito.
<pre>
fiberhome = Fiberhome('<b>IP_DA_OLT</b>', '<b>USUARIO</b>', '<b>SENHA</b>')
fiberhome.make_ftp_backup("<b>IP_SERVIDOR_FTP</b>", "<b>USUARIO_FTP</b>", "<b>SENHA_FTP</b>", "<b>/DIR_FTP/ARQUIVO</b>-{}.cfg".format(bkday))
</pre>
