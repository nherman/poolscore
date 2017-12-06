/* tourney.js */

define('components/tourney', ['knockout','services/api',], function(ko, api) {

    'use strict';

    ko.components.register('tourney-component', {
        viewModel: tourneyViewModel,
        template: { require: 'text!partials/tourney.html' }
    });

    return tourneyViewModel;

    function tourneyViewModel(options) {
        var self = this;

        if (options.tourney_id === undefined || !options.tourney_id.match(/^\d+$/)) {
            throw "Invalid Tourney ID";
        }

        if (options.rootVM === undefined) {
            throw "Missing rootVM reference";
        }

        function getTourney() {
            api.getTourney(options.tourney_id, function(json) {
                console.log(json);
                self.raw = json["tourney"];

                self.date(self.raw.date);
                self.winner_id(self.raw.winner_id);
                self.home_score(self.raw.home_score || 0);
                self.away_score(self.raw.away_score || 0);

                self.home_team(self.raw.home_team);
                self.away_team(self.raw.away_team);
            });
        }

        function getMatches() {
            api.getMatches(options.tourney_id, function(json) {
                console.log(json);
                self.matches(json["matches"]);
            });
        }

        self.tourney_id = options.tourney_id;

        self.raw = {};
        self.date = ko.observable();
        self.winner_id = ko.observable();
        self.home_score = ko.observable();
        self.away_score = ko.observable();

        self.home_team = ko.observable();
        self.away_team = ko.observable();

        self.matches = ko.observableArray();
        /* generate data object for match_player_template */
        /* TODO: convert to knockout custom binding */
        self.getMatchPlayerData = function(team) {
            var team_id = self[team + '_team']().team_id;
            team_id = team_id.substring(team_id.length-2, team_id.length);
            return {
                team: team,
                team_id: team_id
            };
        };

        /* TODO: refactor new Match into singleton */
        self.lagger = ko.observable();
        self.nonLagger = ko.observable();
        self.newMatch = function() {
            var lagger, nonLagger, data = {
                    "match":{
                        "events": {
                            "lag": null
                        },
                        "home_players": [],
                        "away_players": []
                    }
                };

            function _p(o) {
                var a = o.split('-');
                return {
                    "team": a[0],
                    "id": a[1]
                };
            }

            //validate select value format
            if (!self.lagger().match(/.+-\d+/) || !self.nonLagger().match(/.+-\d+/)) return;

            //parse team and player id from select values
            lagger = _p(self.lagger());
            nonLagger = _p(self.nonLagger());

            //validate players from different teams
            if (lagger.team == nonLagger.team) return;

            //populate data
            data.match[lagger.team + '_players'].push(lagger.id);
            data.match[nonLagger.team + '_players'].push(nonLagger.id);
            data.match.events.lag = lagger.team;

            api.createMatch(options.tourney_id, data,
                function(json) {
                    //reset form
                    self.lagger(-1);
                    self.nonLagger(-1);

                    getMatches();
                }
            );

        }

        // self.events = {};

        //initialize view model
        getTourney();
        getMatches();

    }


});