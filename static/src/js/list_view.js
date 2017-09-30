/**
 * Created by HuangHongLiang on 2016/11/25.
 */
var ListView = function (model, listHolderID, listCellHtml) {
    this.model = model;
    this.listCellHtml = listCellHtml;
    this.listHolderID = listHolderID;
    this.pageSize = 30;
    this.currentPage = 0;
    this.virtualListView = null;
    this.fields = null;
    this.domain = [];
    this.isLoading = false;
    this.init = function () {
        var self = this;
        self.fields = this.getFields();
        self.domain = [];
        this.virtualListView = f7App.virtualList('#' + this.listHolderID, {
            items: [],
            height: function (item) {
                return 44;
            },
            renderItem: function (index, item) {
                return self.renderItem(index, item);
            }
        });
        self.currentPage = 0;
        $('.infinite-scroll').on('infinite', function () {
            if (self.isLoading) {
                return;
            }
            if (self.currentPage > 100) {
                $('.infinite-scroll-preloader').hide();
                return;
            }
            self.isLoading = true;
            setTimeout(function () {
                self.isLoading = false;
                $('.infinite-scroll-preloader').hide();
            }, 20000);
            self.currentPage += 1;
            self.loadData(self.fields, self.domain, self.currentPage);
        });


        var refreshContent = $('.pull-to-refresh-content');
        refreshContent.on('refresh', function () {
            self.refresh();
        });
        f7App.pullToRefreshTrigger(refreshContent);
        $(".center").on('click', function () {
            $(".page-content").scrollTop(0, 200, function () {

            })
        });
    }

    this.refresh = function () {
        var self = this;
        self.currentPage = 0;
        self.loadData(self.fields, self.domain, self.currentPage);
        setTimeout(function () {
            f7App.pullToRefreshDone();
        }, 20000);
    }
    this.renderItem = function (index, dataIem) {
        for (var key in dataIem) {
            var val = dataIem[key];
            if (val.constructor == Array && val.length == 2) {
                dataIem[key] = val[1];
            }
        }
        var itemHtml = Template7.templates.listCell(dataIem);
        itemHtml = itemHtml.replace(/[\r\n]/g, "");
        itemHtml = itemHtml.trim();
        $(itemHtml).find(".f7-item-details").attr('data-id', dataIem['id']);
        return itemHtml;
    }

    this.renderListView = function (list) {
        if (this.currentPage == 0) {
            this.virtualListView.deleteAllItems();
        }
        this.virtualListView.appendItems(list);
    }

    this.onItemDetails = function () {
        alert(this);
    }

    this.loadData = function (fields, domain, page) {
        var self = this;
        odoo.rpcCall(self.model, 'search_read', [domain, fields], {offset: page * self.pageSize, limit: self.pageSize}, function (result) {
            self.isLoading = false;
            f7App.pullToRefreshDone();
            $('.infinite-scroll-preloader').hide();
            self.renderListView(result);
            $(".infinite-scroll-preloader").hide();
            $(".f7-item-details").off('click', self.onItemDetails);
            $(".f7-item-details").on('click', self.onItemDetails);
        }, function () {
            self.isLoading = false;
            f7App.pullToRefreshDone();
            $('.infinite-scroll-preloader').hide();
        });
    }

    this.getFields = function () {
        var fields = this.listCellHtml.match(/{{\w+}}/g)
        var finalFields = [];
        if (fields && fields.length > 0) {
            for (var i = 0; i < fields.length; i++) {
                var fName = fields[i].replace("{{", "").replace("}}", "");
                finalFields[finalFields.length] = fName;
            }
        }
        return finalFields;
    }
}

function _init_list_view_page_() {
    var listCellHtml = $("#listCell").html();
    var model = $("#model").val();
    if (listCellHtml && model) {
        var listView = new ListView(model, "list-view", listCellHtml);
        listView.init();
    }
}

_init_list_view_page_();