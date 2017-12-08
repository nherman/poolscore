/* main.js */

define('pages/main', ['knockout', 'services/utils', 'components/tourney', 'components/match'], function(ko, utils) {

    'use strict';

    return mainViewModel;

    /* main
     * routing for child vms
     * header/breadcrumb content
     */

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

            var data = path.match(/(match|game)\/([^\/]+)/),
                _componentOptions = defaultComponentOptions;

            if (data != null) {
                _componentOptions.name = data[1] + "-component";
                _componentOptions.params.match_id = data[2];
            }

            self.mainComponent(_componentOptions);
        }

        self.headerContent = ko.computed(function() {
            var html = "Tourney <span class='badge'>" + _options.tourney_id + "</span>";

            // html += " : Match <span class='badge'>" + _options.match_id + "</span>";
            // html += " : Game <span class='badge'>" + _options.game_id + "</span>";

            return html;
        });

        /* navigate to new page */
        self.viewTrourney = function(tourney) {
            self.routes.go(); //reset route
        }
        self.viewMatch = function(match) {
            self.routes.go('/match/' + match.id);
        }
        self.viewGame = function(game) {
            self.routes.go('/game/' + game.id);
        }

        self.mainComponent = ko.observable();

        utils.routes.call(self, {
            onRouteChange: routeHandler
        });

    }

});