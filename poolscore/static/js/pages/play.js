define(['jquery',
        'knockout',
        'services/api',
        'services/utils',
        'services/alerts',
        'services/entity'],
function($, ko, api, utils, alerts, entity) {

    'use strict';

    return ViewModel;

    function addMatchViewModel(options) {
        var self = this,
            options = ko.utils.extend({
                "tourney_id": undefined,
                "home_players": [],
                "away_players": [],
                "onAdd": function() {}
            }, options);

        function _isEmpty(v) { return (v == undefined || v == null || v == "" || v == -1);}

        function _getPlayerId(o) {
            a = o.split('_');
            return {
                "team": a[0],
                "id": a[1]
            }
        }

        function _getPlayerSelectItem(p, team) {
            return {
                "value":team + "_" + p.id,
                "label":p.last_name + ", " + p.first_name + " (" + p.handicap + ")",
                "team": team
            };
        }

        self.selectItems = {
            "home": [],
            "away": []
        };

        self.lag_winner = ko.observable();
        self.lag_loser = ko.observable();

        self.resetForm = function() {
            self.lag_winner(-1);
            self.lag_loser(-1);
        };

        self.canAdd = ko.computed(function() {
            var wid, lid;
            if (_isEmpty(self.lag_winner()) || _isEmpty(self.lag_loser())) {
                return false;
            }
            wid = _getPlayerId(this.lag_winner());
            lid = _getPlayerId(this.lag_loser());
            if(wid.id == lid.id || wid.team == lid.team) return false;
            return true;
        }, self)

        self.init = function(initOptions) {
            initOptions = initOptions || {};
            options = ko.utils.extend(options, initOptions);

            ko.utils.arrayForEach(options.home_players, function(p) {
                self.selectItems.home.push(_getPlayerSelectItem(p, 'home'));
            });
            ko.utils.arrayForEach(options.away_players, function(p) {
                self.selectItems.away.push(_getPlayerSelectItem(p, 'away'));
            });
        }

        self.add = function() {
            var data = {
                    "match":{
                        "events": {
                            "lag": null
                        }
                    },
                    "home_players": [],
                    "away_players": []
                };

            function _populateData(p,w) {
                var o = _getPlayerId(p);
                data[o.team + '_players'].push(o.id);
                if (w) {
                    data.match.events.lag = o.team;
                }
            }

            if (!self.canAdd()) return;

            _populateData(this.lag_winner(),true);
            _populateData(this.lag_loser(),false);


            api.createMatch(options.tourney_id, data,
                function(json) {
                    self.resetForm();
                    options.onAdd(json);
                    //TODO create game
                }
            );
        };

    }

    function ViewModel(tourney_id) {
        var self = this,
            matches_endpoint,
            initTemplateOptions = {
                "name": ""
            },
            headerTemplateOptions = {
                "name": "header_template",
                "data": {}
            },
            matchTemplateOptions = {
                "name": "match_template",
                "data": {}
            };


        /* initialize templates */
        self.headerTemplateOptions = ko.observable(initTemplateOptions);
        self.matchTemplateOptions = ko.observable(initTemplateOptions);

        /* Render Add Match Form */
        self.addMatchViewModel = new addMatchViewModel({
            "tourney_id": tourney_id,
            "onAdd": function(resp) {
                var match, matchJSON = resp.match || resp;
                if (typeof matchJSON == "object" && matchJSON.id !== undefined) {
                    match = new entity.Match(matchJSON.id, {
                        "json": matchJSON,
                        "tourney": self.tourney
                    });
                    match.addGame();
                    self.matches.push(match);
                }
            }
        });


        /* populate Tourney model */
        self.tourney = new entity.Tourney(tourney_id, {

            /* Tourney onInit callback */
            "callback": function() {

                /* update add match form to include available players */
                self.addMatchViewModel.init({
                    "home_players": self.tourney.home_team.players,
                    "away_players": self.tourney.away_team.players
                });

                /* render templates */
                headerTemplateOptions.data = self.tourney;
                self.headerTemplateOptions(headerTemplateOptions);

                matchTemplateOptions.data = self;
                self.matchTemplateOptions(matchTemplateOptions);
            }
        });

        /* get all Matches */
        self.matches = ko.observableArray();

        api.getMatches(tourney_id,
            function(json) {
                if (json === undefined || typeof json != "object") return;

                ko.utils.arrayForEach(json["matches"], function(match){
                    self.matches.push(new entity.Match(match.id, {
                        "json": match,
                        "tourney": self.tourney
                    }));
                });
            }
        );

        /* display game edit view */
        self.editGame = function(game) {
            self.matchTemplateOptions({
                "name": "edit_game_template",
                "data": game
            });
        };

        self.displayMatch = function() {
            self.matchTemplateOptions(matchTemplateOptions);
        };

    }

});