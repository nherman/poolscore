define(['jquery',
        'knockout'],
function($, ko) {

    // 'use strict';


window.PS = window.PS || (function() {
    var root = "/api/v1.0/";
        endpoints = {
            "tourneys": _m("tourneys","tourney/tourneys.json"),
            "tourneyCount": _m("count","tourney/count.json"),
            "tourney": _m("tourney", "tourney%s/%s.json"),
            "user": _m("user", "users/%s.json")
        };

    function _m(n,p) {
        return {"path":p,"node":n};
    }

    function _p() {
        var i=0, path = arguments[i++];
        if (path === undefined) return "";

        while(i < arguments.length) {
            path = path.replace(/%s/,arguments[i++]);
        }

        if (path.indexOf(root) != 0) {
            path = root + path;
        }

        return path;
    }

    return {
        "models": {},
        "endpoints": endpoints,
        "getPath": _p
    };

})();

window.PS.alertsModel = (function() {
    var self, timeoutHandle,
        defaultAlertTemplateOptions = {
            "name": "",
            "data": {}
        },
        alertTemplateName = "alert_template",
        elm = "#alerts",
        topOffset = 32,
        showAnimationSpeed = 1000,
        hideAnimationSpeed = 400,
        duration = 5000;

    function _showAlert() {
        /* Update the view - generates DOM elements*/
        self.alertTemplateOptions({
            "name": alertTemplateName,
            "data": ko.mapping.fromJS(self.alerts.shift())
        });

        $(elm).animate({
            top: topOffset,
            opacity: 1
        },
        showAnimationSpeed);

        timeoutHandle = setTimeout(function() {
            _hideAlert();
        }, duration);
    }

    function _hideAlert() {
        $(elm).animate({
            top: 0,
            opacity: 0,
        },
        hideAnimationSpeed,
        function() {
            self.alertTemplateOptions(defaultAlertTemplateOptions);
        });
    }

    function _cancelAlert() {
        if (_isAlertActive()) {
            clearTimeout(timeoutHandle);
            _hideAlert();
        }
    }

    function _clearAllAlerts() {
        _cancelAlert();
        self.alerts.length = 0;
    }

    function _addAlert(options) {
        options = $.extend({
            "type": "warning"
        }, options);

        self.alerts.push({
            "css": "alert alert-dismissible alert-" + options.type,
            "content": options.content,
            "cancel": _cancelAlert
        });
    }

    function _isAlertActive() {
        return self.alertTemplateOptions().name == alertTemplateName;
    }

    self = {
        "alerts": [],
        "alertTemplateOptions": ko.observable(defaultAlertTemplateOptions),
        "add": _addAlert,
        "clear": _clearAllAlerts,
        "isActive": _isAlertActive
    };

    /* poll for new alerts */
    setInterval(function() {
        if (self.alerts.length > 0 && !_isAlertActive()) {
            _showAlert();
        }
    },100);

    return self;
})();
ko.applyBindings(window.PS.alertsModel, document.getElementById('alerts'));


window.PS.loaderModel = (function() {
    var self;

    function _t(bool) {
        self.isLoading(bool);
    }

    self = {
        "content": "Loading&hellip;",
        "isLoading": ko.observable(false),
        "showLoader": function() {
            _t(true);
        },
        "hideLoader": function() {
            _t(false);
        }
    }

    $( document ).ajaxStart(function() {
        self.showLoader()
    });

    $( document ).ajaxStop(function() {
        self.hideLoader()
    });

    return self;

})();
ko.applyBindings(window.PS.loaderModel, document.getElementById('loading'));


window.PS.sModel = function(config) {
    var self = this;

    /* process config */
    self.modelName = config.modelName || "viewModel";
    self.apiMap = $.extend({
            "entities": undefined,
            "entityCount": undefined,
            "entity": undefined,
        }, config.apiMap || {});

    /* knockout observables */
    self.entities = ko.observableArray();
    self.entityCount = ko.observable(0);
    self.displayPagination = ko.observable(true);
    self.page = ko.observable(1);
    self.entitiesPerPage = ko.observable(25);
    self.entitySort = ko.observable("date_modified desc");
    self.selectedEntity = ko.observable();


    /* private methods */
    function _getPage(increment) {
        var page = this.page() + increment;
        if (page > this.pages() || page < 1) return;
        _updateEntities(this.selectedGroup(), {
            "page":page
        });
        this.page(page);
    }


    function _updateEntities(group, params) {
        var entityNode = "",
            entityUrl = "",
            countNode = "",
            countUrl = "",
            data = {
                "limit": self.entitiesPerPage(),
                "page": "1",
                "order": self.entitySort()
            };

        if (params !== undefined && params instanceof Object) {
            $.extend(data, params);
        }

        entityUrl = window.PS.getPath(self.apiMap.entities.path);
        entityNode = self.apiMap.entities.node

        countUrl = window.PS.getPath(self.apiMap.entityCount.path);
        countNode = self.apiMap.entityCount.node;

        $.getJSON( countUrl, function( json ) {
            if (json[countNode] !== undefined) {
                self.entityCount(json[countNode]);
            }
        });

        $.getJSON( entityUrl, data, function( json ) {
            if (json[entityNode] !== undefined && json[entityNode] instanceof Array) {
                self.entities(json[entityNode]);
            }
        });
    }

    $.extend(self, {
        /* public methods */

        pages: ko.computed(function() {
            return Math.ceil(self.entityCount() / self.entitiesPerPage()) || 1;
        }),

        getPreviousPage: function() {
            _getPage.call(this, -1);
        },

        getNextPage: function() {
            _getPage.call(this, 1);
        },

        refreshPage: function() {
            _getPage.call(this, 0);
        },

        selectEntity: function(entity_id, callback) {
            var url, node;

            if (entity_id == undefined) {

                self.selectedEntity(undefined);

            } else {

                url = window.PS.getPath(self.apiMap.entity, entity_id),
                node = self.apiMap.entity.node;

                $.getJSON( url, function( json ) {
                    if (json[node] !== undefined) {
                        self.selectedEntity(json[node]);
                        if (typeof callback == "function") {
                            callback();
                        }
                    }
                });
            }
        },

        clearSelectedEntity: function() {
            self.selectEntity();
        },

        init: function( callback, options ) {
            _updateEntities();
            if (callback != undefined && typeof callback == "function") {
                callback();
            }
        }
    });
};

console.log('main');

/* binds enter key to function */
// ko.bindingHandlers.enterkey = {
//     init: function (element, valueAccessor, allBindings, viewModel) {
//         var callback = valueAccessor();
//         $(element).keypress(function (event) {
//             var keyCode = (event.which ? event.which : event.keyCode);
//             if (keyCode === 13) {
//                 callback.call(viewModel);
//                 return false;
//             }
//             return true;
//         });
//     }
// };

});
