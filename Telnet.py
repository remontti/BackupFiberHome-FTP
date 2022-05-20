#!/usr/bin/python3
import socket
import re
import time


class Telnet:
    sock = None
    host = None
    user = None
    password = None

    def __init__(self, host, user, passwd, port=23, code="iso-8859-1", userattr="Login", passedattr="Password",
                 lged="User"):
        self.host = host
        self.code = code
        self.user = user
        self.password = passwd
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        validated = False
        if self.check_response(userattr):
            self.send_command(self.user)
            if self.check_response(passedattr):
                self.send_command(self.password)
                if self.check_response(lged):
                    validated = True
        if not validated:
            raise ValueError("Authentication Failed")

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.sock.close()
        exit()

    def send_command(self, command: object) -> object:
        self.sock.send("{}\n".format(command).encode())

    def recv_all(self, buffersize=512):
        data = ''
        while True:
            time.sleep(1)
            response = self.sock.recv(buffersize)
            response_text = response.decode(self.code)
            data += response_text
            if len(response) < buffersize:
                break
        return data

    def recv_response(self, buffersize=1024):
        response = self.sock.recv(buffersize)
        return response.decode(self.code)

    def recv_raw_response(self, buffersize=1024):
        return self.sock.recv(buffersize)

    def check_response(self, attr, timeout=2):
        response = self.recv_all()
        match = re.search(r'(.*?' + attr + '*)', response)
        if match:
            return response
        counter = 0
        while not match:
            response = self.recv_response()
            match = re.search(r'(.*?' + attr + '*)', response)
            if match:
                return response
            counter += 1
            if counter == timeout:
                return None
            time.sleep(1)
