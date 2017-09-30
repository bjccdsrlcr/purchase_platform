/**
 * Created by HuangHongLiang on 2016/1/28.
 */
var LocalData = function () {
    var self = this;
    this.isLocalStorageSupport = function () {
        var testKey = 'test', storage = window.localStorage;
        try {
            storage.setItem(testKey, '1');
            storage.removeItem(testKey);
            return true;
        } catch (error) {
            return false;
        }
    }

    this.put = function (key, data) {
        if (self.isLocalStorageSupport()) {
            data = JSON.stringify(data);
            window.localStorage.setItem(key, data);
        } else {
            console.error("do not support local storage");
        }
    }

    this.get = function (key, defaultValue) {
        var result = null;
        if (self.isLocalStorageSupport()) {
            result = localStorage[key];
            if(result) {
                result = JSON.parse(result);
            }
        } else {
            console.error("do not support local storage");
        }
        if(!result){
            result = defaultValue;
        }
        return result;
    }
};

