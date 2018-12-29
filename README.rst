MQ PHP HTTP SDK
===============

Alyun MQ Documents: http://www.aliyun.com/product/ons

Aliyun MQ Console: https://ons.console.aliyun.com

Requires
--------

Python version: [2.5,3.0)

Install sdk by pip
------------------

1. install pip, see
   `document <https://pip.pypa.io/en/stable/installing/>`__
2. install sdk by pip

.. code:: bash

   pip insall mq_http_sdk

Notice
------

MQClient, Producer, Consumer are not thread safe, please use multi
instance in mutli thread.

Samples
-------

Publish Message
~~~~~~~~~~~~~~~

.. code:: python

   #!/usr/bin/env python
   # coding=utf8

   from mq_http_sdk.mq_exception import MQExceptionBase
   from mq_http_sdk.mq_producer import *
   from mq_http_sdk.mq_client import *

   #初始化 client
   mq_client = MQClient(
       #设置HTTP接入域名（此处以公共云生产环境为例）
       "${HTTP_ENDPOINT}",
       #AccessKey 阿里云身份验证，在阿里云服务器管理控制台创建
       "${ACCESS_KEY}",
       #SecretKey 阿里云身份验证，在阿里云服务器管理控制台创建
       "${SECRET_KEY}"
       )
   #所属的 Topic
   topic_name = "${TOPIC}"
   #Topic所属实例ID，默认实例为空None
   instance_id = "${INSTANCE_ID}"

   producer = mq_client.get_producer(instance_id, topic_name)

   # 循环发布多条消息
   msg_count = 100
   print "%sPublish Message To %s\nTopicName:%s\nMessageCount:%s\n" % (10 * "=", 10 * "=", topic_name, msg_count)

   try:
       for i in range(msg_count):
           msg_body = "I am test message %s." % i
           msg = TopicMessage(
               # 消息内容
               "I am test message %s." % i, 
               # 消息标签
               ""
           )
           re_msg = producer.publish_message(msg)
           print "Publish Message Succeed. MessageID:%s, BodyMD5:%s" % (re_msg.message_id, re_msg.message_body_md5)
           time.sleep(1)
   except MQExceptionBase, e:
       if e.type == "TopicNotExist":
           print "Topic not exist, please create it."
           sys.exit(1)
       print "Publish Message Fail. Exception:%s" % e

Consume Message
~~~~~~~~~~~~~~~

.. code:: python

   #!/usr/bin/env python
   # coding=utf8

   from mq_http_sdk.mq_exception import MQExceptionBase
   from mq_http_sdk.mq_consumer import *
   from mq_http_sdk.mq_client import *

   #初始化 client
   mq_client = MQClient(
       #设置HTTP接入域名（此处以公共云生产环境为例）
       "${HTTP_ENDPOINT}",
       #AccessKey 阿里云身份验证，在阿里云服务器管理控制台创建
       "${ACCESS_KEY}",
       #SecretKey 阿里云身份验证，在阿里云服务器管理控制台创建
       "${SECRET_KEY}"
     )
   #所属的 Topic
   topic_name = "${TOPIC}"
   #您在控制台创建的 Consumer ID(Group ID)
   group_id = "${GROUP_ID}"
   #Topic所属实例ID，默认实例为空None
   instance_id = "${INSTANCE_ID}"

   consumer = mq_client.get_consumer(instance_id, topic_name, group_id)

   #长轮询表示如果topic没有消息则请求会在服务端挂住3s，3s内如果有消息可以消费则立即返回
   #长轮询时间3秒（最多可设置为30秒）
   wait_seconds = 3
   #一次最多消费3条(最多可设置为16条)
   batch = 3
   print "%sConsume And Ak Message From Topic%s\nTopicName:%s\nMQConsumer:%s\nWaitSeconds:%s\n" % (10 * "=", 10 * "=", topic_name, group_id, wait_seconds)
   while True:
       try:
           #长轮询消费消息
           recv_msgs = consumer.consume_message(batch, wait_seconds)
           for msg in recv_msgs:
               print "Receive, MessageId: %s\nMessageBodyMD5: %s \
                                 \nMessageTag: %s\nConsumedTimes: %s \
                                 \nPublishTime: %s\nBody: %s \
                                 \nNextConsumeTime: %s \
                                 \nReceiptHandle: %s" % \
                                (msg.message_id, msg.message_body_md5,
                                 msg.message_tag, msg.consumed_times,
                                 msg.publish_time, msg.message_body,
                                 msg.next_consume_time, msg.receipt_handle)
       except MQExceptionBase, e:
           if e.type == "MessageNotExist":
               print "No new message! RequestId: %s" % e.req_id
               continue

           print "Consume Message Fail! Exception:%s\n" % e
           time.sleep(2)
           continue

       #5分钟之内若不确认消息消费成功，则消息会重复消费
       try:
           receipt_handle_list = [msg.receipt_handle for msg in recv_msgs]
           consumer.ack_message(receipt_handle_list)
           print "Ak %s Message Succeed.\n\n" % len(receipt_handle_list)
       except MQExceptionBase, e:
           print "\nAk Message Fail! Exception:%s" % e
           #某些消息的句柄可能超时了会导致确认不成功
           if e.sub_errors:
             for sub_error in e.sub_errors:
               print "\tErrorHandle:%s,ErrorCode:%s,ErrorMsg:%s" % (sub_error["ReceiptHandle"], sub_error["ErrorCode"], sub_error["ErrorMessage"])
