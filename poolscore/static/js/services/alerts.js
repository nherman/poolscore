/* 
 * KO Alerts Mixin
 * Enable Alerts in KO view model.
 *
 * Assumes alert HTML bound to viewmodel includes a block like: data-bind="foreach: alerts.list()" 
 * 
 * Usage:
 * alerts.call(vm);
 * vm.alerts.add({
    temp: true,
    duration: "optional milliseconds (only if temp = true)"
    header: "optional text string",
    body: "optional html string,
    type: "info|warning|success|danger"
 })
 */

define(['jquery',
        'knockout'],
function($, ko) {

    'use strict';

    return function() {
        /* 
         * Private members
         */
        var self = this,
            _nextId = 0,
            _defaultDuration = 5000,
            _alerts = ko.observableArray(),

            common_error_options = {
                type: "danger",
                header: "<span class='icon-danger'></span>Error",
                body: DEFAULT_ERROR_TEXT || ""
            },

            common_success_options = {
                type: "success",
                header: "<span class='icon-success'></span>Success",
            };

        function _alert(options) {
            options = options || {};
            this.temp = options.temp || false;
            this.header = options.header || "";
            this.body = options.body || "";
            this.type = options.type || "info";
            this.id = _nextId++;
            this.css = {
                "alert": true
            }
            this.css["alert-" + this.type] = true;

            this.dismiss = function() {
                _dismissAlert(this.id);
            }
        }

        function _addAlert(options) {
            /* create alert and insert into queue */
            var newalert,
                options = ko.utils.extend({
                    temp: false,
                    duration: _defaultDuration
                }, options);

            newalert = new _alert(options);
            _alerts.unshift(newalert);

            if (options.temp) {
                setTimeout(function() {
                    _dismissAlert(newalert.id);
                }, options.duration);
            }
        }

        function _dismissAlert(id) {
            _alerts.remove(function(item) {
                return item.id == id;
            });
        }

        function _clearAlerts() {
            _alerts.removeAll();
        }

        function _commonAlertFactory(factory_options) {
            var factory_options = ko.utils.extend({
                clear: false,
                temp: true,
                type: "info"
            }, factory_options);

            return function(options) {
                var options = ko.utils.extend(factory_options, options);

                if (options.clear) {
                    _removeAll();
                }
                _addAlert(options);                    
            }

        }

        /* hide alerts if we're showing a bootstrap modal */
        $(document).on('show.bs.modal', function() {
           _clearAlerts();
        });


        /* expose api */
        self.alerts = {
            list: _alerts,
            add: _addAlert,
            dismiss: _dismissAlert,
            removeAll: _clearAlerts,
            error: _commonAlertFactory(common_error_options),
            success: _commonAlertFactory(common_success_options)
        };
    }
});
