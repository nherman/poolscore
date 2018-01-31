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
            }, options);

        function routeHandler(path, payload) {
            //path: entity/id || entity/id/entity/id || ""

            var data = path.match(/(match|game)\/([^\/]+)/g),
                _componentOptions = {
                    'name':'tourney-component',
                    'params': {
                        'rootVM': self,
                        'tourney_id':_options.tourney_id
                    }
                };


            // data == [] or ["match/1"] or ["match/1", "game/2"]
            while (data !== null && data.length > 0) {
                var pair = data.shift().split('/');
                _componentOptions.name = pair[0] + "-component";
                _componentOptions.params[pair[0]+"_id"] = pair[1];
            }

            self.mainComponent(_componentOptions);
            self.headerContent(
                buildHeaderContent(_componentOptions.params)
            );

        }

        function buildHeaderContent(options) {
            var path = "#",
                html = "<a href='" + path + "'>Tourney</a>";

            options = ko.utils.extend({
                "match_id": "",
                "game_id": ""
            }, options);

            if (options.match_id !== "") {
                path += "/match/" + options.match_id;
                html += " : <a href='" + path + "'>Match <span class='badge'>" + options.match_id + "</span></a>";
            }
            if (options.game_id !== "") {
                path += "/game/" + options.game_id;
                html += " : <a href='" + path + "'>Game <span class='badge'>" + options.game_id + "</span></a>";
            }

            return html;
        }

        /* observables */
        self.mainComponent = ko.observable();
        self.headerContent = ko.observable();


        /* navigate to new page */
        self.viewTourney = function(tourney) {
            self.routes.go(); //reset route
        }
        self.viewMatch = function(match) {
            self.routes.go('/match/' + match.id);
        }
        self.viewGame = function(game) {
            self.routes.go('/game/' + game.id);
        }

        utils.routes.call(self, {
            onRouteChange: routeHandler
        });

    }

});