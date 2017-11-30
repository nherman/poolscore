/* 
 * KO Routes Mixin
 * Enable Routing in KO view model
 * 
 * Usage (w/ tabs):
 * mixins.routes.call(vm, {
 *     onRouteChange: function(path, payload) {
 *        var tab = self.tabbing.get(payload);
 *        if (tab !== undefined) {
 *            self.tabbing.go(tab);
 *        }
 *     }
 * });
 * 
 */

define("services/utils", ['knockout'], function(ko) {

    'use strict';

    var utils = {};

    utils.routes = routes;
    utils.isEmpty = isempty;

    return utils;

    function isempty(v) {
        return (v == undefined || v == null || v == "");
    }

    function routes(options) {
        /* 
         * Private members
         */
        var self = this,
            _options = ko.utils.extend({
                routes: undefined,
                onRouteChange: function() {},
                defaultPath: ''
            }, options),
            _routes = [],
            _path = ko.observable();

        function _parseHash() {
            var h = window.location.hash.slice(1) || '/';

            _path(h);
        }

        function _onRouteChange(path) {
            if (typeof _options.onRouteChange === "function") {
                _options.onRouteChange(path, _getPayload());
            }
        }

        function _getPayload() {
            return _routes[_path()];
        }

        function _addRoute(path, payload) {
            if (payload !== undefined) {
                _routes[path] = payload;
            }
        }

        function _executeRoute(path) {
            window.location.hash = path;
        }

        /*
         * Constructor
         */
        _path.extend({ notify: 'always' });
        _path.subscribe(_onRouteChange);

        /* instantiate listeners */
        ko.utils.registerEventHandler(window, "hashchange", _parseHash);
        ko.utils.registerEventHandler(window, "load", _parseHash);

        /* expose api */
        self.routes = {
            get: _getPayload,
            add: _addRoute,
            go: _executeRoute,
            path: _path
        };

        /* execute routes one time if the onLoad event has already fired */
        if (document.readyState === "complete") {
            _parseHash();
        }

    }

});
