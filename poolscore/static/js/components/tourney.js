/* tourney.js */

define('components/tourney', ['knockout','services/api',], function(ko, api) {

    'use strict';

    ko.components.register('tourney-component', {
        viewModel: tourneyViewModel,
        template: { require: 'text!partials/tourney.html' }
    });

    return tourneyViewModel;

    function tourneyViewModel(options) {
        var self = this,
            MAX_MATCHES = 5;

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

        function updateTourney(data, callback) {
            var _data = {
                "tourney": ko.utils.extend({
                    "winner_id": self.winner_id(),
                    "home_score": self.home_score(),
                    "away_score": self.away_score()
                }, data)
            };

            api.updateTourney(options.tourney_id, _data, callback);
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
        self.getMatchPlayerData = function(match, team) {
            var data = {
                    team_id:"",
                    player_name:"",
                    games_needed:"",
                    games_won:"",
                    points:"",
                },

                long_team_id = self[team + '_team']().team_id,
                player = (match[team + '_players'] && match[team + '_players'][0]) ? match[team + '_players'][0] : "";

            data.team_id = long_team_id.substring(long_team_id.length-2, long_team_id.length);
            data.player_name = player.last_name + ", " + player.first_name;
            data.games_needed = match[team + '_games_needed'];
            data.games_won = match[team + '_games_won'];
            data.points = match[team + '_score'];

            return data;
        };

        /* TODO: refactor new Match into singleton */
        self.lagger = ko.observable();
        self.nonLagger = ko.observable();
        self.newMatchAllowed = ko.computed(function() {
            console.log(self.matches().length < MAX_MATCHES);
            return self.matches().length < MAX_MATCHES;
        });
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

            if (!self.newMatchAllowed()) return;

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

        self.endTourney = function() {
            /* set winner id, unless there's a tie */
            if (self.home_score() > self.away_score()) {
                self.winner_id(self.home_team().id);
            }
            if (self.home_score() < self.away_score()) {
                self.winner_id(self.away_team().id);
            }

            updateTourney({"active":false}, function(json) {
                location.href="/";
            });
        }

        self.winnerName = ko.computed(function() {
            if (self.home_score() > self.away_score()) {
                return self.home_team().name;
            }
            if (self.home_score() < self.away_score()) {
                return self.away_team().name;
            }
            return null;
        });
        self.winnerScore = ko.computed(function() {
            return Math.ceil(self.home_score(), self.away_score());
        });
        self.loserScore = ko.computed(function() {
            return Math.floor(self.home_score(), self.away_score());
        });

        //initialize view model
        getTourney();
        getMatches();

    }


});