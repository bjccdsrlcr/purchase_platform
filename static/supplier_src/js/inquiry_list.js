/**
 @项目: wensfood
 @模块名称
 @Copyright 2016 WENS <www.wens.com.cn>
 @Created by LiJiaJie at 2017/1/12 下午2:26
 **/

var mCurrentPage = 0;//当前页
var mIsLoading = false;
var lineHeight = 80;
var mListView = null;

/**
 * @功能描述: 初始化
 * @作者: 黎嘉杰
 * @日期: 2017-01-12
 */
function init() {
     enableCsrfValidation = false;
    //绑定虚拟列表
    bindVirtualList();
    //绑定搜索栏
    bindSearchBar();
    //加载列表
    loadList();
}

/**
 * @功能描述: 绑定搜索栏
 * @作者: 黎嘉杰
 * @日期: 2017-01-12
 */
function bindSearchBar(){
    mySearchbar = myApp.searchbar(
        '.searchbar',
        {
            customSearch: true,
            onSearch:function(){
                //输入后， 重新加载列表
                loadList();
            }
        }
    );
}

/**
 * @功能描述: 绑定虚拟列表
 * @作者: 黎嘉杰
 * @日期: 2017-01-12
 */
function bindVirtualList() {
    mListView = myApp.virtualList('#notice-list', {
        items: [],
        height: function (item) {
            return lineHeight;
        },
        renderItem: function (index, item) {
            return renderItem(index, item);
        },
    });

    var refreshContent = $('.pull-to-refresh-content');
    refreshContent.off('refresh');
    refreshContent.on('refresh', function (e) {
        mCurrentPage = 0;
        console.log("执行了下拉刷新");
        myApp.pullToRefreshDone();
        loadList();
        setTimeout(function () {
            myApp.pullToRefreshDone();
        }, 20000);
    });
}


/**
 * @功能描述: 渲染公告行
 * @作者: 黎嘉杰
 * @日期: 2017-01-12
 */
function renderItem(index, item) {
    var itemHtml = Template7.templates.noticeItem(item);
    itemHtml = itemHtml.replace(/[\r\n]/g, "");
    itemHtml = itemHtml.trim();
    return itemHtml;
}

/**
 * @功能描述: 加载数据
 * @作者: 黎嘉杰
 * @日期: 2017-01-12
 */
function loadList(){
    var txt = $('#search-input').val();
    var params = {
        'page': mCurrentPage,
        'txt' : txt
    };
    odoo.api("/ws/wx/getinquirys", params, function (result){
        mIsLoading = false;
        myApp.pullToRefreshDone();

        if (mCurrentPage == 0) {
            mListView.deleteAllItems();
        }

        mListView.appendItems(result);

        $(".infinite-scroll-preloader").hide();
    });
}
$('.infinite-scroll').on('infinite', function () {
    if (mIsLoading) {
        return;
    }
    if (mCurrentPage > 10) {
        $('.infinite-scroll-preloader').hide();
        return;
    }
    mIsLoading = true;
    setTimeout(function () {
        mIsLoading = false;
        $('.infinite-scroll-preloader').hide();
    }, 20000);
    mCurrentPage++;
    loadList();
});

function onView_home() {
    window.location = '/ws/wx/inquiry_list?t=' + new Date().getTime()
    // mainView.router.reloadPage('/ws/wx/inquiry_list?t=' + new Date().getTime());

}
$.ajax({
    type: 'post',
    url: '/ws/wx/getinquirys',
    success:function (data) {
        data = JSON.parse(data)
        console.log(data)
    }
});
function onView(inquiryid) {
    //?supplierid=' + supplierid + "&inquiryid="+inquiryid+"&t=" + new Date().getTime(),
    console.log(inquiryid)
    mainView.router.load({
        'url': '/ws/wx/inquiry_selinfo?inquiryid='+inquiryid+"&t=" + new Date().getTime(),
        'reload': false,
        'animatePages': true,
        'pushState': false
    });
    mainView.router.refreshPage('/ws/wx/inquiry_selinfo?inquiryid='+inquiryid+"&t=" + new Date().getTime());
    var interval = window.setInterval(function(){
        var timer = $("#timer");
        if(timer.html() == undefined){
            clearInterval(interval);
            return;
        }
        var end_time=$("#end_time").val();
        end_time = end_time.replace(/\-/g, "/");
        var now = new Date();
        var endDate = new Date(end_time);
        var leftTime=endDate.getTime()-now.getTime();
        if(leftTime<=0){
            timer.html("已结束");
            return;
        }
        var leftsecond = parseInt(leftTime/1000);
        var day1=Math.floor(leftsecond/(60*60*24));
        var hour=Math.floor((leftsecond-day1*24*60*60)/3600);
        var minute=Math.floor((leftsecond-day1*24*60*60-hour*3600)/60);
        var second=Math.floor(leftsecond-day1*24*60*60-hour*3600-minute*60);
        timer.html(day1+"天"+hour+"小时"+minute+"分"+second+"秒");

    }, 1000);
}

function onViewInfo(ilineid,inquiryid) {
    mainView.router.load({
            'url': '/ws/wx/inquiry_info?ilineid=' + ilineid +"&inquiryid="+inquiryid+ "&t=" + new Date().getTime(),
            'reload': false,
            'animatePages': true,
            'pushState': true
        });
    var interval2 = window.setInterval(function(){
        var timer = $("#timer2");
        if(timer.html() == undefined){
            clearInterval(interval2);
            return;
        }
        var end_time=$("#end_time").val();
        end_time = end_time.replace(/\-/g, "/");
        var now = new Date();
        var endDate = new Date(end_time);
        var leftTime=endDate.getTime()-now.getTime();
        if(leftTime<=0){
            timer.html("已结束");
            return;
        }
        var leftsecond = parseInt(leftTime/1000);
        var day1=Math.floor(leftsecond/(60*60*24));
        var hour=Math.floor((leftsecond-day1*24*60*60)/3600);
        var minute=Math.floor((leftsecond-day1*24*60*60-hour*3600)/60);
        var second=Math.floor(leftsecond-day1*24*60*60-hour*3600-minute*60);
        timer.html(day1+"天"+hour+"小时"+minute+"分"+second+"秒");

    }, 1000);
}


function onViewInfo2(placeid,inquiryid) {
    // for(i=0; i< placeid.length;i++){
    //     console.log(placeid.charAt(i));
    //     if (placeid.charAt(i) == '+'){
    //         console.log(i)
    //     }
    // }
    //inquiryid = inquiryid.replace(/\+/g, '%2B')
    mainView.router.load({
            'url': '/ws/wx/inquiry_info?placeid='+ encodeURIComponent(placeid) +'&inquiryid='+ inquiryid+ "&t=" + new Date().getTime(),
            'reload': false,
            'animatePages': true,
            'pushState': true
        });
    console.log('placeid', placeid);
    console.log('inquiryid', inquiryid);

    var interval3 = window.setInterval(function(){
        var timer = $("#timer2");
        if(timer.html() == undefined){
            clearInterval(interval3);
            return;
        }
        var end_time=$("#end_time").val();
        end_time = end_time.replace(/\-/g, "/");
        var now = new Date();
        var endDate = new Date(end_time);
        var leftTime=endDate.getTime()-now.getTime();
        if(leftTime<=0){
            timer.html("已结束");
            return;
        }
        var leftsecond = parseInt(leftTime/1000);
        var day1=Math.floor(leftsecond/(60*60*24));
        var hour=Math.floor((leftsecond-day1*24*60*60)/3600);
        var minute=Math.floor((leftsecond-day1*24*60*60-hour*3600)/60);
        var second=Math.floor(leftsecond-day1*24*60*60-hour*3600-minute*60);
        timer.html(day1+"天"+hour+"小时"+minute+"分"+second+"秒");

    }, 1000);
}

function onBack(flag) {
    mainView.router.back({'reload': true, 'animatePages': true});
}

function onSubmit(ilineid,cfdeliverytype,cfdeliveryway,cfunitid,inquiryid) {
    var timerval = $("#timer2").html();
    if(timerval == "已结束"){
        myApp.alert("报价已结束，不能再报","提示");
        return;
    }
    //交货类型
    var delivery_category_num = $("#delivery_category_num").val();
    //交货地点
    var sel_trading_place_id = $("#sel_trading_place_id").val();
    //产地
    var sel_oplace = $("#sel_oplace").val();
    //包装
    var txt_package = $("#txt_package").val();
    //交货期
    var sel_delivery_period_id = $("#sel_delivery_period_id").val();
    //交货价格
    var txt_out_price = $("#txt_out_price").val();
    //合约
    var sel_contract_num_id = $("#sel_contract_num_id").val();
    //基差
    var txt_basediff = $("#txt_basediff").val();

    if(sel_trading_place_id == "请选择"){
        myApp.alert("交货地点不能为空","提示");
        return;
    }
    if(sel_oplace == "请选择"){
        myApp.alert("产地不能为空","提示");
        return;
    }
    if(txt_package == ""){
        myApp.alert("包装不能为空","提示");
        return;
    }
    if(delivery_category_num=="002"){
        if(sel_delivery_period_id == "请选择"){
            myApp.alert("交货期不能为空","提示");
            return;
        }
        if(txt_out_price == "" && txt_basediff == ""){
            myApp.alert("一口价和基差不能为空","提示");
            return;
        }
        if(txt_out_price == "" && txt_basediff != "" && sel_contract_num_id == ""){
            myApp.alert("合约不能为空","提示");
            return;
        }
    }else{
        if(txt_out_price == ""){
            myApp.alert("交货地报价不能为空","提示");
            return;
        }
    }



    var storedData = myApp.formToJSON('#inquiry_form');

    console.log('ilineid',ilineid);
    storedData['ilineid'] = ilineid;
    storedData['cfdeliverytype'] = cfdeliverytype;
    storedData['cfdeliveryway'] = cfdeliveryway;
    storedData['cfunitid'] = cfunitid;
    storedData['inquiryid'] = inquiryid;
    console.log('storedData', storedData);
    console.log('storedData', storedData.ilineid);
    if(storedData) {
        odoo.api("/ws/wx/inquiry_save", storedData, function (data){
           myApp.alert("提交成功!","提示")
            var inquiryid = data;
            onView(inquiryid);

        });
    }else {
        alert('There is no stored data for this form yet. Try to change any field')
    }
}

init();