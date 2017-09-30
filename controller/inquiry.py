# coding=utf-8
# ==============================================================
# project:      wensfood
# module:       stash
# author:       YangYongde
# email:        913789598@qq.com
# create_date:  2017-06-07
# description:  .
# license: Copyright. All Rights Reserved. WENS.
# ==============================================================
import json
import os
import time
import urllib
import urllib2
import sys
import re
import httplib2 as httplib2
import simplejson
import werkzeug

from jinja2 import Environment, FileSystemLoader
from odoo import http
from odoo.http import request
from odoo.tools import config
reload(sys)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
template_loader = FileSystemLoader(searchpath=BASE_DIR + "/template")
jinja = Environment(loader=template_loader)
sys.setdefaultencoding('utf-8')


class MainController(http.Controller):

    #询价单List
    @http.route('/ws/wx/inquiry_list', type='http')
    def inquiry_list(self, **kwargs):
        template = jinja.get_template("inquiry_list.html")
        html = template.render()
        return html

    # 询价单list内容
    @http.route('/ws/wx/getinquirys', type='http', csrf=False)
    def getinquirys(self, **kwargs):
        user = request.env.user
        eas_suplier_fid = user.partner_id.eas_supplier_fid.id
        eas_suplier_fid = urllib.quote(eas_suplier_fid)
        if eas_suplier_fid == None:
            raise Exception
        url = config.get('easapi_url', None)
        openurl = '%s/ws/pur/solution/getinquirys?supplierid=%s' % (url, eas_suplier_fid)
        res_fb = urllib.urlopen(openurl)
        result_text_fb = res_fb.read()
        jsonval_fb = json.loads(result_text_fb)
        jsonres_fb = json.loads(jsonval_fb['result'])
        result =[]
        cfdeliveryway_switcher = {
            '1': u'自提',
            '2': u'到港',
            '4': u'到厂'
        }
        cfdeliverytype_switcher = {
            '1': u'现货',
            '2': u'远期',
        }
        for num in range(0,len(jsonres_fb)):
            jsonres_fb[num]['cfdeliveryway'] = cfdeliveryway_switcher.get(jsonres_fb[num]['cfdeliveryway'])
            jsonres_fb[num]['cfdeliverytype'] = cfdeliverytype_switcher.get(jsonres_fb[num]['cfdeliverytype'])
            result.append(jsonres_fb[num])
        data =  {
            "code":0,
            "msg":"ok",
            "data": result,
        }
        return simplejson.dumps(data)

    #所选中询价单详情
    @http.route('/ws/wx/inquiry_selinfo', type='http')
    def inquiry_selinfo(self, **kwargs):
        template = jinja.get_template("inquiry_selinfo.html")
        user = request.env.user
        url = config.get('easapi_url')
        eas_inquiryid = urllib.quote(kwargs.get('inquiryid'))
        eas_supplierid = urllib.quote(user.partner_id.eas_supplier_fid.id)
        openurl = '%s/ws/pur/solution/getinquiryinfo?supplierid=%s&inquiryid=%s'%(url, eas_supplierid,eas_inquiryid)
        res_fb = urllib.urlopen(openurl)
        result_text_fb = res_fb.read()
        jsonval_fb = json.loads(result_text_fb)
        jsonres_inquiry = json.loads(jsonval_fb['result'])
        jsonres_entrys = json.loads(jsonval_fb['entrys'])
        cfdeliveryway_switcher = {
            '1': u'自提',
            '2': u'到港',
            '4': u'到厂'
        }
        cfdeliverytype_switcher = {
            '1': u'现货',
            '2': u'远期',
        }
        #用于前端显示，否则只会显示1,2/1,2,4
        jsonres_inquiry['cfdeliveryway_name'] = cfdeliveryway_switcher.get(jsonres_inquiry['cfdeliveryway'])
        jsonres_inquiry['cfdeliverytype_name'] = cfdeliverytype_switcher.get(jsonres_inquiry['cfdeliverytype'])

        #分组，对于同个交货地点有不同的交货期，且可以有多个交货地点的实现
        group_places = []
        if jsonres_entrys:
            group_places.append(jsonres_entrys[0])
        else:
            group_places = []
        for iline in jsonres_entrys:
                addflag = 1
                for gplace in group_places:
                    if (iline['pid'] == gplace['pid']):
                        addflag = 0
                        break
                if (addflag == 1):
                    group_places.append(iline)
        # 前端显示合约号以及交货期，否则只显示id值
        contract_nums = []
        for num in range(0, len(jsonres_entrys)):
            contract_nums = request.env['ws_pp.eas_treaty'].sudo().search([('fid', '=', jsonres_entrys[num]['cftreatyid'])])
            periodid = request.env['ws_pp.eas_period'].sudo().search([('fid', '=', jsonres_entrys[num]['cfperiodid'])])
            if contract_nums:
                jsonres_entrys[num]['cftreatyid_name'] = contract_nums.fname_l2
            else:
                jsonres_entrys[num]['cftreatyid_name'] = None
            if periodid:
                jsonres_entrys[num]['cfperiodid_name'] = periodid.fnumber
            else:
                jsonres_entrys[num]['cfperiodid_name'] = None

        data = {
            'group_places':group_places,
            "jsonres_inquiry": jsonres_inquiry,
            "jsonres_entrys": jsonres_entrys,
            'contract_nums': contract_nums
        }
        html = template.render(data=data)
        return html

    #询价单详情
    @http.route('/ws/wx/inquiry_info', type='http')
    def inquiry_info(self, **kwargs):
        template = jinja.get_template("inquiry_info.html")
        ilineid = kwargs.get('ilineid')
        print kwargs.get('placeid')
        data = {}
        eas_supplierid = urllib.quote(request.env.user.partner_id.eas_supplier_fid.id)
        url = config.get('easapi_url')
        # ilineid = None 表示新增报价明细
        if ilineid is None:
            # 取到交货地点的id ###################继续报价
            placeid = kwargs.get('placeid')
            place = None
            if placeid:
                place = request.env['ws_pp.eas_place'].sudo().search([('fid', '=', placeid)])

            eas_inquiryid = urllib.quote(kwargs.get('inquiryid'))
            openurl = '%s/ws/pur/solution/getinquiryinfo?supplierid=%s&inquiryid=%s'\
                      % (url, eas_supplierid, eas_inquiryid)
            res_fb = urllib.urlopen(openurl)
            result_text_fb = res_fb.read()
            jsonval_fb = json.loads(result_text_fb)
            jsonres_inquiry = json.loads(jsonval_fb['result'])
            jsonres_entrys = json.loads(jsonval_fb['entrys'])
            # 自提，到港，到厂
            deliveryway = jsonres_inquiry['cfdeliveryway']
            ptype = "0"
            if (deliveryway == "1"):
                ptype = "0"
            elif (deliveryway == "2"):
                ptype = "1"
            elif (deliveryway == "4"):
                ptype = "2"
            #根据deliveryway的种类来显示相对应的交货地点，见需求文档
            #将停用的交货地点删除
            place_lines = []
            pattern = re.compile(ur'（停用）')
            dplaces = request.env['ws_pp.eas_place'].sudo().search([('cftype', '=', ptype)], 0, 999)
            for item in dplaces:
                error_place = pattern.findall(item['fname_l2'])
                if error_place:
                    place_lines = place_lines
                else:
                    place_lines.append(item)
            originPlaces = request.env['ws_pp.eas_originplace'].sudo().search([('flevel', '=', 1)])
            contract_nums = request.env['ws_pp.eas_treaty'].sudo().search([])
            cur_time = time.strftime('%Y%m', time.localtime(time.time()))
            deliperiods = request.env['ws_pp.eas_period'].sudo().search([('fnumber', '>=', cur_time)],
                                                                         )
            data = {
               'originPlaces':originPlaces,
               'deliperiods':deliperiods,
               'place_lines': place_lines,
               'jsonres_inquiry': jsonres_inquiry,
               'jsonres_entrys': jsonres_entrys,
               'contract_nums':contract_nums,
               'place':place
            }
        # 修改报价明细
        else:
            place=''
            eas_inquiryid = urllib.quote(kwargs.get('inquiryid'))
            openurl = '%s/ws/pur/solution/getinquiryinfo?supplierid=%s&inquiryid=%s'\
                      % (url, eas_supplierid, eas_inquiryid)
            res_fb = urllib.urlopen(openurl)
            result_text_fb = res_fb.read()
            jsonval_fb = json.loads(result_text_fb)
            jsonres_inquiry = json.loads(jsonval_fb['result'])
            jsonres_entrys = json.loads(jsonval_fb['entrys'])
        # 根据ilineid判断需要修改的报价明细
            for num in range(0, len(jsonres_entrys)):
                if jsonres_entrys[num]['fid'] == ilineid:
                    jsonres_entrys = jsonres_entrys[num]
                    break
            # 自提，到港，到厂
            deliveryway = jsonres_inquiry['cfdeliveryway']
            ptype = "0"
            if (deliveryway == "1"):
                ptype = "0"
            elif (deliveryway == "2"):
                ptype = "1"
            elif (deliveryway == "4"):
                ptype = "2"
            place_lines = []
            pattern = re.compile(ur'（停用）')
            dplaces = request.env['ws_pp.eas_place'].sudo().search([('cftype', '=', ptype)], 0, 999)
            for item in dplaces:
                error_place = pattern.findall(item['fname_l2'])
                if error_place:
                    place_lines = place_lines
                else:
                    place_lines.append(item)
            originPlaces = request.env['ws_pp.eas_originplace'].sudo().search([('flevel', '=', 1)])
            contract_nums = request.env['ws_pp.eas_treaty'].sudo().search([])
            cur_time = time.strftime('%Y%m', time.localtime(time.time()))
            deliperiods = request.env['ws_pp.eas_period'].sudo().search([('fnumber', '>=',cur_time)],
                                                                        )
            data = {
               'originPlaces': originPlaces,
               'deliperiods': deliperiods,
               'place_lines': place_lines,
               'jsonres_inquiry': jsonres_inquiry,
               'jsonres_entrys': jsonres_entrys,
               'contract_nums': contract_nums,
                'place': place
            }
        html = template.render(data=data)
        return html

    #询价单保存
    @http.route('/ws/wx/inquiry_save', type='http',csrf=False)
    def inquiry_save(self, **kwargs):
        #询价单ID
        ilineid = kwargs.get('ilineid')
        inquiryid = kwargs.get('inquiryid')
        eas_ilineid = urllib.quote(ilineid)
        eas_inquiryid = urllib.quote(inquiryid)
        user = request.env.user
        supplierid = user.partner_id.eas_supplier_fid.id
        eas_supplierid = urllib.quote(supplierid)
        url = config.get('easapi_url')
        openurl = '%s/ws/pur/solution/getinquiryinfo?supplierid=%s&inquiryid=%s' % (url, eas_supplierid, eas_inquiryid)
        res_fb = urllib.urlopen(openurl)
        result_text_fb = res_fb.read()
        jsonval_fb = json.loads(result_text_fb)
        jsonres_entrys = json.loads(jsonval_fb['entrys'])
        eas_delivery_period_id = ''
        eas_treatyid = ''
        eas_basediff = ''
        delivery_pid = kwargs.get('sel_trading_place_id')
        cfperoidid = kwargs.get('sel_delivery_period_id')
        # 交货地点
        eas_delivery_pid = urllib.quote(delivery_pid)
        # 交货地报价
        eas_delivery_place_price = urllib.quote(kwargs.get('txt_out_price'))
        # utf-8编码
        pkgname = kwargs.get('txt_package')
        utf8_pkgname = pkgname.encode("utf-8")
        remark = kwargs.get('txt_remark')
        utf8_remark = remark.encode('utf-8')
        # 产地
        eas_origin_place = urllib.quote(kwargs.get('sel_oplace'))
        # 包装
        eas_pkname = urllib.quote(utf8_pkgname)
        # 可供数量
        eas_maxqty = urllib.quote(kwargs.get('txt_amount'))
        # 备注
        eas_remark = urllib.quote(utf8_remark)
        # 交货类型
        eas_deliverytype = urllib.quote(kwargs.get('cfdeliverytype'))
        # 交货方式
        eas_deliveryway = urllib.quote(kwargs.get('cfdeliveryway'))
        # 计量单位
        eas_unitid = urllib.quote(kwargs.get('cfunitid'))
        data_error ={}
        # 询价单如果是远期 增加合约基差交货期
        if kwargs.get('cfdeliverytype') == '2':
            # 合约
            eas_treatyid = urllib.quote(kwargs.get('sel_contract_num_id'))
            # 基差
            eas_basediff = urllib.quote(kwargs.get('txt_basediff'))
            # 交货期
            eas_delivery_period_id = urllib.quote(cfperoidid)
            # 对于同一交货地点，同一交货期，只能有一条报价记录
            for num in range(0, len(jsonres_entrys)):
                if (jsonres_entrys[num]['cfperiodid'] == cfperoidid) and (jsonres_entrys[num]['pid'] == delivery_pid) and ilineid == '':
                     result = '此交货地该交货期已报价!'
                     data_error = {
                        'code':500,
                        'msg':'此交货地该交货期已报价!',
                        'data': result
                        }
                     break
        # 询价单交货类型为现货
        if kwargs.get('cfdeliverytype') == '1':
            # 对于同一交货地点，只能有一条报价记录
            for num in range(0, len(jsonres_entrys)):
                if (jsonres_entrys[num]['pid'] == delivery_pid) and ilineid == '':
                     result = '该交货地已报价!'
                     data_error = {
                        'code':500,
                        'msg':'该交货地已报价!',
                        'data': result
                        }
                     break
        params = {
                 'fparentid': eas_inquiryid,
                 'cfsupplierid': eas_supplierid,
                 'cfdeliveryplaceid': eas_delivery_pid,
                 'cforiginplaceid': eas_origin_place,
                 'cfpkname': eas_pkname,
                 'cfdeliveryway': eas_deliveryway,
                 'cfdeliverytype': eas_deliverytype,
                 'cfperiodid':eas_delivery_period_id,
                 'cfprice': eas_delivery_place_price,
                 'cfunitid': eas_unitid,
                 'cftreatyid': eas_treatyid,
                 'cfbasediff': eas_basediff,
                 'cfmaxqty': eas_maxqty,
                 'cfremark': eas_remark
                }
        # 如果ilineid存在，即是更新数据库记录，需要增加fid
        if ilineid:
            params['fid'] = eas_ilineid
            params = urllib.urlencode(params)
        # 反之，向数据库插入记录，不需要fid
        else:
            params = urllib.urlencode(params)

        url = config.get('easapi_url')
        openurl = '%s/ws/pur/solution/inquiry_save'%(url)

        if data_error:
            data = data_error
        else:
            ret = urllib.urlopen(url=openurl, data=params)
            code = ret.getcode()
            print 'code', code
            ret_data = ret.read()
            print ret_data
            print inquiryid
            data = {
                "code": 0,
                "msg": "提交成功!",
                "data": inquiryid
            }

        return simplejson.dumps(data)

