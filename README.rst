MQ Python HTTP SDK
==================

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

   pip install mq_http_sdk

Notice
------

MQClient, Producer, Consumer are not thread safe, please use multi
instance in mutli thread.

Samples
-------

`Publish
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/producer.py>`__

`Consume
Message <https://github.com/aliyunmq/mq-http-samples/blob/master/python/consumer.py>`__
