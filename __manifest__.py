# -*- coding: utf-8 -*-
# 项目: ws_purchase
# 文件:
# Copyright 2017 WENS <www.wens.com.cn>
# Created by garvey at 2017/5/18 10:58

{
    'name': 'WENS_PURCHASE_SUPLIER',
    'summary': '供应商门户',
    'version': '1.0',
    'category': 'WENSAPPLICATION',
    'sequence': 10,
    'author': 'Huang Ming Liang',
    'website': 'http://www.wens.com.cn',
    'images': [],
    'depends': ['ws_purchase_base',
    ],
    'data': [
        'views/inquiry_info.xml',
        'views/supplier_quotes.xml',
        'views/tender_round.xml',
        'views/menu.xml',
    ],
    'qweb': [

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'description': u"""
        供应商门户
    """
}