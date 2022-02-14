# coding=utf-8
import asyncio
import ssl
from logging import Logger
from typing import Optional, Union

import certifi

import aiohttp
from aiohttp.http_exceptions import BadStatusLine

from .mq_exception import *

DEFAULT_CONNECTION_TIMEOUT = 60
DEFAULT_READ_TIMEOUT = 100


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


class MQHTTPAsyncConnection:
    def __init__(self, host: str, connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT):
        self.host = host
        self.connection_timeout = connection_timeout
        self.session = aiohttp.ClientSession(base_url=f"http://{host}", timeout=connection_timeout, raise_for_status=True)

    async def renew_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = aiohttp.ClientSession(base_url=f"http://{self.host}", timeout=self.connection_timeout,
                                             raise_for_status=True)

    def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


class MQHTTPSAsyncConnection:
    def __init__(self, host: str, ca_cert: str):
        self.host = host
        self.ca_cert = ca_cert
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_verify_locations(ca_cert)
        self.connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(base_url=f"https://{host}", raise_for_status=True, connector=self.connector)

    async def renew_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = aiohttp.ClientSession(base_url=f"https://{self.host}", raise_for_status=True, connector=self.connector)

    def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


class MQAsyncHttp:
    def __init__(self, host: str, connection_timeout: Optional[int] = DEFAULT_CONNECTION_TIMEOUT, keep_alive: Optional[bool] = True, logger: Optional[Logger] = None, is_https: Optional[bool] = False, read_timeout: Optional[int] = DEFAULT_READ_TIMEOUT):
        ca_cert = certifi.where()
        self.is_https = ca_cert and is_https
        self.timeout = aiohttp.ClientTimeout(sock_read=read_timeout, sock_connect=connection_timeout)
        if self.is_https:
            self.conn = MQHTTPSAsyncConnection(host, ca_cert=ca_cert)
        else:
            self.conn = MQHTTPAsyncConnection(host, connection_timeout=connection_timeout)
        self.host = host
        self.is_https = is_https
        self.connection_timeout = connection_timeout
        self.keep_alive = keep_alive
        self.logger = logger
        if self.logger:
            self.logger.info("InitOnsHttp KeepAlive:%s ConnectionTime:%s" % (self.keep_alive, self.connection_timeout))

    def set_log_level(self, log_level: Union[str, int]):
        if self.logger:
            self.logger.setLevel(log_level)

    def close_log(self):
        self.logger = None

    def set_connection_timeout(self, connection_timeout: int):
        self.connection_timeout = connection_timeout
        if not self.is_https:
            if self.conn and self.conn.session and not self.conn.session.closed:
                asyncio.run(self.conn.session.close())
            self.conn = MQHTTPAsyncConnection(self.host, connection_timeout=connection_timeout)

    def set_keep_alive(self, keep_alive: bool):
        self.keep_alive = keep_alive

    def is_keep_alive(self):
        return self.keep_alive

    async def send_request(self, req_inter: RequestInternal) -> ResponseInternal:
        try:
            if self.logger:
                self.logger.debug("SendRequest %s" % req_inter)
            try:
                async with self.conn.session.request(method=req_inter.method, url=req_inter.uri, data=req_inter.data,
                                                     headers=req_inter.header, ssl=False,
                                                     timout=self.timeout) as http_resp:
                    resp_inter = ResponseInternal(status=http_resp.status, header=http_resp.headers, data=await http_resp.text())
            except BadStatusLine:
                await self.conn.renew_session()
                async with self.conn.session.request(method=req_inter.method, url=req_inter.uri, data=req_inter.data,
                                                     headers=req_inter.header, ssl=False,
                                                     timout=self.timeout) as http_resp:
                    resp_inter = ResponseInternal(status=http_resp.status, header=http_resp.headers, data=await http_resp.text())
            if not self.is_keep_alive():
                await self.conn.session.close()
            if self.logger:
                self.logger.debug("GetResponse %s" % resp_inter)
            return resp_inter
        except Exception as e:
            await self.conn.session.close()
            raise MQClientNetworkException("NetWorkException", str(e))  # raise netException
