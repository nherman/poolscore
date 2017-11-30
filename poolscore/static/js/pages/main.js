/* main.js */

define('pages/main', ['knockout', 'services/utils', 'components/tourney'], function(ko, utils) {

    'use strict';

    return mainViewModel;

    function mainViewModel(options) {
        var self = this,
            _options = ko.utils.extend({
                "tourney_id": "",
                "match_id": "",
                "game_id": ""
            }, options),
            defaultComponentOptions = {
                'name':'tourney-component',
                'params': {
                    'rootVM': self,
                    'tourney_id':_options.tourney_id
                }
            };

        function routeHandler(path, payload) {
            //path: entity/id || ""

            var data = path.split('/'),
                _componentOptions = defaultComponentOptions;

            switch (data[0]) {
                case "match":
                    _componentOptions.name = "match-component";
                    _componentOptions.params.match_id = data[1];
                    break;
                case "game":
                    _componentOptions.name = "game-component";
                    _componentOptions.params.game_id = data[1];
                    break;
            }

            self.mainComponent(_componentOptions);
        }

        self.headerContent = ko.computed(function() {
            var html = "Tourney <span class='badge'>" + _options.tourney_id + "</span>";

            // html += " : Match <span class='badge'>" + _options.match_id + "</span>";
            // html += " : Game <span class='badge'>" + _options.game_id + "</span>";

            return html;
        });

        self.mainComponent = ko.observable();

        utils.routes.call(self, {
            onRouteChange: routeHandler
        });

    }

});