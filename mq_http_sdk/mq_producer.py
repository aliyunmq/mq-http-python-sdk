# coding=utf-8

from mq_request import *

try:
    import json
except ImportError, e:
    import simplejson as json


class MQProducer:
    def __init__(self, instance_id, topic_name, mq_client, debug=False):
        if instance_id is None:
            self.instance_id = ""
        else:
            self.instance_id = instance_id
        self.topic_name = topic_name
        self.mq_client = mq_client
        self.debug = debug

    def set_debug(self, debug):
        self.debug = debug

    def publish_message(self, message):
        """ 发送消息

            @type message: TopicMessage object
            @param message: 发布的TopicMessage object

            @rtype: TopicMessage object
            @return: 消息发布成功的返回属性，包含MessageId和MessageBodyMD5

            @note: Exception
            :: MQClientParameterException  参数格式异常
            :: MQClientNetworkException    网络异常
            :: MQServerException           处理异常
        """
        req = PublishMessageRequest(self.instance_id, self.topic_name, message.message_body, message.message_tag)
        resp = PublishMessageResponse()
        self.mq_client.publish_message(req, resp)
        self.debuginfo(resp)
        return self.__publish_resp2msg__(resp)

    def debuginfo(self, resp):
        if self.debug:
            print "===================DEBUG INFO==================="
            print "RequestId: %s" % resp.header["x-mq-request-id"]
            print "================================================"

    def __publish_resp2msg__(self, resp):
        msg = TopicMessage()
        msg.message_id = resp.message_id
        msg.message_body_md5 = resp.message_body_md5
        return msg


class TopicMessage:
    def __init__(self, message_body="", message_tag=""):
        """ Specify information of TopicMessage

            @note: publish_message params
            :: message_body        string
            :: message_tag         string, used to filter message

            @note: publish_message response information
            :: message_id
            :: message_body_md5
        """
        self.message_body = message_body
        self.message_tag = message_tag

        self.message_id = ""
        self.message_body_md5 = ""

    def set_message_body(self, message_body):
        self.message_body = message_body

    def set_message_tag(self, message_tag):
        self.message_tag = message_tag
