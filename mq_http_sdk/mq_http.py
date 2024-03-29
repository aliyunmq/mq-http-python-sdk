# coding=utf-8

import socket
import sys
from .mq_exception import *
if sys.version > '3':
    from http.client import HTTPConnection, BadStatusLine, HTTPSConnection
else:
    from httplib import HTTPConnection, BadStatusLine, HTTPSConnection


class MQHTTPConnection(HTTPConnection):
    def __init__(self, host, port=None, strict=None, connection_timeout=60):
        HTTPConnection.__init__(self, host, port, strict)
        self.request_length = 0
        self.connection_timeout = connection_timeout

    def send(self, str):
        HTTPConnection.send(self, str)
        self.request_length += len(str)

    def request(self, method, url, body=None, headers={}):
        self.request_length = 0
        HTTPConnection.request(self, method, url, body, headers)

    def connect(self):
        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port, 0,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                self.sock.settimeout(self.connection_timeout)
                if self.debuglevel > 0:
                    print("connect: (%s, %s)" % (self.host, self.port))
                self.sock.connect(sa)
            except socket.error as e:
                msg = e
                if self.debuglevel > 0:
                    print('connect fail:', (self.host, self.port))
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error(msg)

class MQHTTPSConnection(HTTPSConnection):
    def __init__(self, host, port=None, strict=None):
        HTTPSConnection.__init__(self, host, port, strict=strict)
        self.request_length = 0

    def send(self, str):
        HTTPSConnection.send(self, str)
        self.request_length += len(str)

    def request(self, method, url, body=None, headers={}):
        self.request_length = 0
        HTTPSConnection.request(self, method, url, body, headers)


class MQHttp:
    def __init__(self, host, connection_timeout=60, keep_alive=True, logger=None, is_https=False):
        if is_https:
            self.conn = MQHTTPSConnection(host)
        else:
            self.conn = MQHTTPConnection(host, connection_timeout=connection_timeout)
        self.host = host
        self.is_https = is_https
        self.connection_timeout = connection_timeout
        self.keep_alive = keep_alive
        self.request_size = 0
        self.response_size = 0
        self.logger = logger
        if self.logger:
            self.logger.info("InitOnsHttp KeepAlive:%s ConnectionTime:%s" % (self.keep_alive, self.connection_timeout))

    def set_log_level(self, log_level):
        if self.logger:
            self.logger.setLevel(log_level)

    def close_log(self):
        self.logger = None

    def set_connection_timeout(self, connection_timeout):
        self.connection_timeout = connection_timeout
        if not self.is_https:
            if self.conn:
                self.conn.close()
            self.conn = MQHTTPConnection(self.host, connection_timeout=connection_timeout)

    def set_keep_alive(self, keep_alive):
        self.keep_alive = keep_alive

    def is_keep_alive(self):
        return self.keep_alive

    def send_request(self, req_inter):
        try:
            if self.logger:
                self.logger.debug("SendRequest %s" % req_inter)
            self.conn.request(req_inter.method, req_inter.uri, req_inter.data, req_inter.header)
            self.conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            try:
                http_resp = self.conn.getresponse()
            except BadStatusLine:
                # open another connection when keep-alive timeout
                # httplib will not handle keep-alive timeout, so we must handle it ourself
                self.conn.close()
                self.conn.request(req_inter.method, req_inter.uri, req_inter.data, req_inter.header)
                self.conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                http_resp = self.conn.getresponse()
            headers = dict(http_resp.getheaders())
            resp_inter = ResponseInternal(status=http_resp.status, header=headers, data=http_resp.read())
            self.request_size = self.conn.request_length
            self.response_size = len(resp_inter.data)
            if not self.is_keep_alive():
                self.conn.close()
            if self.logger:
                self.logger.debug("GetResponse %s" % resp_inter)
            return resp_inter
        except Exception as e:
            self.conn.close()
            raise MQClientNetworkException("NetWorkException", str(e))  # raise netException


class RequestInternal:
    def __init__(self, method="", uri="", header=None, data=""):
        if header == None:
            header = {}
        self.method = method
        self.uri = uri
        self.header = header
        self.data = data

    def __str__(self):
        return "Method: %s\nUri: %s\nHeader: %s\nData: %s\n" % \
               (self.method, self.uri, "\n".join(["%s: %s" % (k, v) for k, v in list(self.header.items())]), self.data)


class ResponseInternal:
    def __init__(self, status=0, header=None, data=""):
        if header == None:
            header = {}
        self.status = status
        self.header = header
        self.data = data

    def __str__(self):
        return "Status: %s\nHeader: %s\nData: %s\n" % \
               (self.status, "\n".join(["%s: %s" % (k, v) for k, v in list(self.header.items())]), self.data)
