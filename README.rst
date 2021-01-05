MQ Python HTTP SDK
==================

Aliyun MQ Documents: http://www.aliyun.com/product/ons

Aliyun MQ Console: https://ons.console.aliyun.com

Requires
--------

Python version(=v1.0.0): [2.5, 3.0)

Python version(>v1.0.0): [2.5, ~)

Install sdk by pip
------------------

1. install pip, see
   `document <https://pip.pypa.io/en/stable/installing/>`__
2. install sdk by pip

.. code:: bash

   pip install mq_http_sdk

Notice
------

MQClient, Producer, Consumer are not thread safe, please use multi
instance in mutli thread.

Note
----

1. Http consumer only support timer msg (less than 3 days), no matter
   the msg is produced from http or tcp protocol.
2. Order is only supported at special server cluster.

Samples (github)
----------------

`Publish
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/producer.py>`__

`Consume
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/consumer.py>`__

`Transaction
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/trans_producer.py>`__

`Publish Order
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/order_producer.py>`__

`Consume Order
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/order_consumer.py>`__

Samples (code.aliyun.com)
-------------------------

`Publish
Message <https://code.aliyun.com/aliware_rocketmq/mq-http-samples/blob/master/python/producer.py>`__

`Consume
Message <https://code.aliyun.com/aliware_rocketmq/mq-http-samples/blob/master/python/consumer.py>`__

`Transaction
Message <https://code.aliyun.com/aliware_rocketmq/mq-http-samples/blob/master/python/trans_producer.py>`__

`Publish Order
Message <https://code.aliyun.com/aliware_rocketmq/mq-http-samples/blob/master/python/order_producer.py>`__

`Consume Order
Message <https://code.aliyun.com/aliware_rocketmq/mq-http-samples/blob/master/python/order_consumer.py>`__
