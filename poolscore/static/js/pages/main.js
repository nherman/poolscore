/* main.js */

define('pages/main', ['knockout', 'utils', 'components/tourney'], function(ko, utils) {

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
                    'tourney_id':_options.tourney_id
                }
            };

        self.mainComponent = ko.observable({
            'name':'tourney-component',
            'params': {
                'tourney_id':_options.tourney_id
            }
        });

        utils.routes.call(self, {
            onRouteChange: function(path, payload) {
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
        });

    }

});