/**
 * odoo的RCP等相关操作。
 * f7App: framework7的实例
 * Created by HuangHongLiang on 2016/1/22.
 */
var Odoo = function (_f7App_) {
    this.rpcCallCount = 1;
    this.app = _f7App_;
    this.$ = Framework7.$;
    var self = this;

    this.rpcCall = function (model, method, args, kwargs, callbackFunc, onFinishedFunc) {
        var url = "/web/dataset/call_kw/" + model + "/" + method;
        self.rpcCallCount += 1;
        var finalParams = {
            id: 9000 + self.rpcCallCount,
            jsonrpc: '2.0',
            method: 'call',
            params: {
                model: model,
                method: method,
                args: args,
                kwargs: kwargs
            }
        }
        //self.ajax("POST", url, finalParams, function (result) {
        self.ajax("POST", url, JSON.stringify(finalParams), function (result) {
            if ("result" in result) {
                callbackFunc(result['result']);
            } else if ('error' in result && 'data' in  result['error'] && 'message' in result['error']['data']) {
                var error = result['error']['data']['message'];
                self.app.alert(error, "提示");
            } else if ("error" in result) {
                self.app.alert("系统出错!", "提示");
            }
            if(onFinishedFunc){
                onFinishedFunc();
            }
        }, true);
    }

    /**
     * 访问API, API的返回值格式为:{code:0,msg:'ok', data: data}, 0表示成功，如果不为0，则表示访问失败。
     * @param url
     * @param params
     * @param success
     */
    this.api = function (url, params, success) {
        console.log(url, params)
        self.ajax("POST", url, params, function (result) {
            if (result['code'] == 0) {
                success(result['data']);
            } else {
                console.log('response code from api:' + result['code'])
                self.app.alert(result['msg'], "提示");
            }
        });
    }

    /**
     * 发送ajax请求
     * @param url
     * @param params
     * @param success
     */
    this.ajax = function (method, url, params, success, isRpc) {
        self.app.showIndicator();
        var p = {
            url: url,
            method: method,
            cache: true,
            data: params,
            //data: JSON.stringify(params),
            dataType: 'text',
            error: function (e) {
                self.rpcCallingCount -= 1;
                console.log("error ajax:" + url);
                try {
                    var result = JSON.parse(e);
                    success(result);
                } catch (ec) {
                    console.log('exception in ajax:' + ec);
                    self.app.alert(e, '错误提示');
                }
            },
            success: function (result) {
                self.rpcCallingCount -= 1;
                console.log("success ajax:" + url);
                self.app.hideIndicator();
                try {
                    var result = JSON.parse(result);
                    success(result);
                } catch (ec) {
                    console.log(ec);
                    self.app.alert(ec, '错误提示');
                }

            },
            complete: function (result, status) {
                console.log("complete ajax:" + url);
                self.app.hideIndicator();
            }
        }
        if(isRpc){
            p['contentType'] = 'application/json';
        }
        self.rpcCallingCount += 1;
        self.$.ajax(p);
    }
};

