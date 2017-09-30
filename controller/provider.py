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

import os
import time

import simplejson
import werkzeug
from jinja2 import Environment, FileSystemLoader
from odoo import http
from odoo.http import request

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
template_loader = FileSystemLoader(searchpath=BASE_DIR + "/template")
jinja = Environment(loader=template_loader)


class MainController(http.Controller):

    #招标List
    @http.route('/ws/wx/provider_list', type='http')
    def provider_list(self, **kwargs):
        template = jinja.get_template("provider_list.html")
        obj = request.env['ws.ps.tender.round']
        curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        user = request.env.user
        suplierid = user.partner_id.id

        supplier = request.env['ws.ps.procurement.solution.supplier'].sudo().search([('supplier_id.id','=',suplierid),('parent_id.begin_time','<=',curtime),('parent_id.end_time','>=',curtime)])
        solutionids = []
        for item in supplier:
            solutionids.append(item.parent_id.id)
        tender_rounds = obj.sudo().search([('start_time','<=',curtime),('end_time','>=',curtime),('procurement_solution_id.id','in',solutionids)])
        html = template.render(data=tender_rounds)
        return html

    #招标List
    @http.route('/ws/wx/provider_info', type='http')
    def provider_info(self, **kwargs):
        template = jinja.get_template("provider_info.html")
        providerid = kwargs.get('providerid', None)
        user = request.env.user
        suplierid = user.partner_id.id
        obj = request.env['ws.ps.tender.round']
        provider_info = obj.sudo().search([('id','=',providerid)])
        isAllow = False
        for item in provider_info.procurement_solution_id.supplier_ids :
            if suplierid == item.supplier_id.id:
                isAllow = True
                break
        #交货地点
        place_lines = []
        for pline in provider_info.procurement_solution_id.place_ids:
            addflag =1
            for iline in provider_info.line_ids:
                if (iline.supplier_id.id == suplierid) and (iline.trading_place_id.id == pline.trading_place_id.id):
                    addflag =0
                    break
            if(addflag == 1):
                place_lines.append(pline)
        #如果不是该供应商，则不显示
        if isAllow != True:
            provider_info = {}
            place_lines = {}
        data={
            'suplierid':suplierid,
            'place_lines':place_lines,
            'provider':provider_info
        }
        html = template.render(data=data)
        return html

    #招标详情
    @http.route('/ws/wx/provider_line', type='http')
    def provider_line(self, **kwargs):
        template = jinja.get_template("provider_line.html")
        ilineid = kwargs.get('ilineid')
        data = {}
        if ilineid is None:
            placeid = kwargs.get('placeid')
            place = request.env['ws.pp.base.place'].sudo().search([('id', '=', placeid)])
            materialid = kwargs.get('materialid')
            material = request.env['ws.pp.base.material'].sudo().search([('id', '=', materialid)])
            providerid = kwargs.get('providerid')
            providerInfo = request.env['ws.ps.tender.round'].sudo().search([('id', '=', providerid)])
            uom_id = kwargs.get('uomid')
            uominfo = request.env['ws.pp.base.unit'].sudo().search([('id', '=', uom_id)])
            iline = {
                'id':'',
                'trading_place_id':place,
                'material_id':material,
                'uom_id':uominfo,
                'amount':'',
                'in_price':'',
                'tran_cost':'',
                'out_price':'',
                'remark':'',
            }
            data = {
               'iline':iline,
               'provider':providerInfo
            }
        else:
            obj = request.env['ws.ps.tender.round.line']
            #当前登陆用户
            user = request.env.user
            suplierid = user.partner_id.id
            iline = obj.sudo().search([('id', '=', ilineid),('supplier_id.id','=',suplierid)])
            data = {
               'iline':iline,
               'provider':iline.parent_id
            }
        html = template.render(data=data)
        return html

    #招标单保存
    @http.route('/ws/wx/provider_save', type='http',csrf = False)
    def provider_save(self, **kwargs):
        lineid = kwargs.get('lineid', None)
        out_price = kwargs.get('out_price', None)
        in_price = kwargs.get('in_price', None)
        tran_cost = kwargs.get('tran_cost', None)
        amount = kwargs.get('amount', None)
        remark = kwargs.get('remark', None)
        materialid = kwargs.get('materialid', None)
        placeid = kwargs.get('placeid', None)
        uom_id = kwargs.get('uom_id', None)
        providerid = kwargs.get('providerid', None)
        solutionid = kwargs.get('solutionid', None)
        user = request.env.user
        suplierid = user.partner_id.id
        vals = {
               'supplier_id':suplierid,
               'trading_place_id':placeid,
               'uom_id':uom_id,
               'material_id':materialid,
               'parent_id':providerid,
               'out_price': out_price,
               'in_price': in_price,
               'tran_cost': tran_cost,
               'amount': amount,
               'inquiry_time':time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
               'remark':remark
        }
        if lineid:
            obj = request.env['ws.ps.tender.round.line'].browse(int(lineid))
            obj.sudo().write(vals)
        else:
            obj = request.env['ws.ps.tender.round.line']
            obj.sudo().create(vals)

        quotes = {
                'procurement_solution_id':solutionid,
                'tender_round_id':providerid,
                'trading_place_id':placeid,
                'supplier_id': suplierid,
                'material_id': materialid,
                'uom_id': uom_id,
                'out_price': out_price,
                'in_price': in_price,
                'tran_cost': tran_cost,
                'amount': amount,
                'inquiry_time':time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
                'quotes_type':'1',
                'inquiry_id':None
            }
        quotesobj = request.env['ws.ps.supplier.quotes']
        quotesobj.sudo().create(quotes)
        return werkzeug.utils.redirect('/ws/wx/provider_info?providerid=%s' % providerid, 303)