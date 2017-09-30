/**
 @项目: wensfood
 @模块名称
 @Copyright 2016 WENS <www.wens.com.cn>
 @Created by LiJiaJie at 2017/1/3 下午2:12
 **/
var myApp = new Framework7({
    precompileTemplates: true,
    'smartSelectBackText': '返回',    //Smart select 页面导航栏中的返回按钮的文案
    'smartSelectPopupCloseText': '关闭',
    'smartSelectPickerCloseText': '确定',
    'modalButtonOk': '确定',
    'modalButtonCancel': '否',
    'modalPreloaderTitle': '加载中...',
    'notificationCloseButtonText': '关闭'
});
var $ = Dom7;

var mainView = myApp.addView('.view-main', {
    dynamicNavbar: true
});

var odoo = new Odoo(myApp);
var localData = new LocalData();