define(['knockout',
        'services/utils',
        'services/api',
        'services/mapping'],
function(ko, utils, api, mapping) {

    'use strict';

    var entity = {
        "Tourney": Tourney,
        "Match": Match,
        "Game": Game
    };

    /* Parent class for Tourney, Match & Game */
    function Entity(id, config) {
        var self = this,
            config = ko.utils.extend({
                "callback": function() {},
                "map_config": {}
            }, config),
            _map_config = {
                'ignore': ['configuration','id','ordinal'],
                'observe': ['data','events'],
                'events': {
                    'create': eventFieldMapHandler,
                    'update': eventFieldMapHandler
                }
            };

        function eventFieldMapHandler(options) {
            var events = options.data
            if(typeof events === "string") {
                events = ko.utils.parseJson(events);
            }
            return ko.observable(mapping.fromJS(events));
        }

        /* merge config.map_config with _map_config and copy merged object to config.map_config */
        for (var key in config.map_config) {
            if (config.map_config.hasOwnProperty(key)) {
                if (config.map_config[key] instanceof Array) {
                    _map_config[key] = _map_config[key].concat(config.map_config[key]);
                } else {
                    _map_config[key] = config.map_config[key];                
                }
            }
        }

        self.id = id;
        self.configuration = config;
        self.configuration.map_config = _map_config;

        self.onBeforeMap();

        /* initialize model data */
        if (typeof self.configuration.json == "object") {
            self.map(self.configuration.json);
            self.onAfterMap(self.configuration.json);
            self.configuration.callback();
        } else {
            self.get(function(json) {
                self.configuration.callback();
            });
        }
    }

    Entity.prototype.onBeforeMap = function() {};
    Entity.prototype.onAfterMap = function() {};

    Entity.prototype.map = function(json) {
        mapping.fromJS(json, this.configuration.map_config, this);
    };

    Entity.prototype.get = function() {
        throw "get method not defined";
    };

    Entity.prototype.update = function() {
        throw "update method not defined";
    };
    function _incEvent(name, num) {
        try {
            this.events()[name](this.events()[name]()*1+num);
            if (this.events()[name]() < 0) {
                /* sanity check: no negative events */
                this.events()[name](0);
                return;
            }
        } catch(e) {
            return;
        }

        this.update();
    }
    Entity.prototype.eventIncrement = function(name) {
        _incEvent.call(this, name, 1);
    }
    Entity.prototype.eventDecrement = function(name) {
        _incEvent.call(this, name, -1);
    }


    function Tourney(id, options) {
        var self = this,
            options = ko.utils.extend({
                "map_config": {
                    'ignore': ['tourneyDate'],
                    'observe': ['date','winner_id','home_score','away_score'],
                    'date': {
                        create: function(options) {
                            self.tourneyDate = ko.computed(function() {
                                /* hack to disregard time zone. Needs to be fixed - probably in the data model */
                                var date = new Date(self.date());
                                var date2 = new Date(date.getTime() + date.getTimezoneOffset()*60*1000);
                                return date2.toDateString();
                            });                    
                            return ko.observable(options.data);
                        }
                    }
                }
            }, options);

        Entity.call(self, id, options);
    }
    Tourney.prototype = Object.create(Entity.prototype);

    Tourney.prototype.onAfterMap = function(json) {
        self.home_team_id = json.home_team_id;
        self.away_team_id = json.away_team_id;
    };

    Tourney.prototype.get = function(callback) {
        var self = this;
        api.getTourney(self.id, function(json) {
            self.map(json["tourney"]);
            self.configuration.json = json["tourney"]; //save raw data
            self.onAfterMap(json["tourney"]);
            if (typeof callback == "function") {
                callback.call(self, json);
            }
        });
    };

    Tourney.prototype.update = function(callback) {
        var self = this,
            data = {};

        /* wrap data in entity name node and remove extraneous objects */
        data["tourney"] = mapping.toJS(self);
        delete data["tourney"].home_team;
        delete data["tourney"].away_team;

        api.updateTourney(self.id, data, function(json) {
            if (typeof callback == "function") {
                callback.call(self, json);
            }
        });
    };

    function Match(id, options) {
        var self = this,
            options = ko.utils.extend({
                "map_config": {
                    'ignore': ['tourney', 'lag_winner', 'lag_loser', 'in_progress', 'games'],
                    'observe': ['home_score','home_games_won','away_score','away_games_won','winner_id']
                }
            }, options);

        self.tourney = options.tourney;
        self.in_progress = ko.observable();
        self.lag_winner = ko.observable();
        self.lag_loser = ko.observable()
        self.games = ko.observableArray();

        self.hasGameInProgress = ko.computed(function() {
            var i=0;
            for (;i<self.games().length;i++) {
                if (self.games()[i].in_progress()) {
                    return true;
                }
            }
            return false;
        });

        self.canAdd = ko.computed(function() {
            var json = options.json;
            return json.home_games_won < json.home_games_needed &&
                json.away_games_won < json.away_games_needed;

        });

        Entity.call(self, id, options);
    }
    Match.prototype = Object.create(Entity.prototype);

    Match.prototype.onAfterMap = function(json) {
        var self = this;

        /* populate games array */
        self.games().length = 0;
        if (json["games"] !== undefined) {
            ko.utils.arrayForEach(json["games"], function(game){
                self.games.push(new Game(game.id, {
                    "tourney": self.tourney,
                    "match": self,
                    "json": game
                }));
            });
        }

        /* get teams */

        /* initialize lag winner/loser */
        lag_team = self.events().lag();
        no_lag_team = (lag_team == "home") ? "away" : "home";
        self.lag_winner(self[lag_team + "_players"][0]);
        self.lag_loser(self[no_lag_team + "_players"][0]);

        self.in_progress(utils.isEmpty(self.winner_id()));
        self.ordinal = self.configuration.json.ordinal;
    };

    Match.prototype.get = function(callback) {
        var self = this;

        api.getMatch(self.tourney.id, self.id,
            function(json) {
                self.map(json["match"]);
                self.configuration.json = json["match"]; //save raw data
                self.onAfterMap(json["match"]);
                if (typeof callback == "function") {
                    callback.call(self, json);
                }
            }
        );
    };

    Match.prototype.update = function(callback) {
        var self = this,
            data = {};

        data["match"] = mapping.toJS(self);

        api.updateMatch(self.tourney.id, self.id, data,
            function(json) {
                if (typeof callback == "function") {
                    callback.call(self, json);
                }
            }
        );
    };

    Match.prototype.updateStatus = function(callback) {
        //
    };

    Match.prototype.addGame = function(callback) {
        var self = this,
            game,
            breaker_id,
            data = {"game":{}};

        if (self.games().length === 0) {

            /* First game. Breaker == lag winner */
            if (self.lag_winner() !== undefined) {
                breaker_id = self.lag_winner().id;
            }

        } else {

            /* Sanity check: one game at a time */
            if (self.games()[self.games().length-1].in_progress()) {
                return;
            }

            /* Sanity check: match complete? */
            if (
                self.configuration.json.home_games_won >= self.configuration.json.home_games_needed ||
                self.configuration.json.away_games_won >= self.configuration.json.away_games_needed
                ) {
                return;
            }

            /* breaker is the last game's winner */
            breaker_id = self.games()[self.games().length-1].winner_id();

        }

        if (breaker_id !== undefined) {
            data["game"]["events"] = {
                "breaker":breaker_id
            };
        }

        api.createGame(self.tourney.id, self.id, data,
            function(json) {
                if (json !== undefined && typeof json === "object" && json.hasOwnProperty('game')) {

                    game = new Game(json.game.id, {
                                    "tourney": self.tourney,
                                    "match": self,
                                    "json": json.game
                                });

                    self.games.push(game);
                }

                if (typeof callback == "function") {
                    callback.apply(self, arguments);
                }
            }
        );
    }

    function Game(id, options) {
        var self = this,
            options = ko.utils.extend({
                "map_config": {
                    'ignore': ['tourney', 'match','in_progress'],
                    'observe': ['winner_id']
                }
            }, options);

        self.tourney = options.tourney;
        self.match = options.match;
        self.in_progress = ko.observable();

        options.callback = function() {
            self.in_progress(utils.isEmpty(self.winner_id()));
            self.in_progress.extend({ notify: 'always' }); //run subscription callbacks if value doesn't change
            self.in_progress.subscribe(function(in_progress) {
                var match = self.match,
                    team,
                    loser;

                if (!self.in_progress()) {
                    /* when the game ends, update the match */

                    /* figure out which team won game*/
                    if (self.winner_id !== undefined) {
                        if (self.winner_id() == match.tourney["home_team_id"]) {
                            team = "home";

                        } else if (self.winner_id() == match.tourney["away_team_id"]) {
                            team = "away";
                        }
                    }

                    /* increment games won */
                    match[team + "_games_won"](match[team + "_games_won"]()+1);

                    if (match[team + "_games_won"]() >= match.configuration.json[team + "_games_needed"]) {
                        /* we have a match winner! set winner_id */
                        match.winner_id(match.tourney[team + "_team_id"]);

                        /* who lost? */
                        loser = (team == "home") ? "away" : "home"

                        if (match[loser + "_games_won"]() == 0) {
                            /* set sweep */
                            match[team + "_score"](3);
                            match.events().sweep(true);
                        } else {
                            match[team + "_score"](2);

                            if (match[loser + "_games_won"]()+1 == match.configuration.json[loser + "_games_needed"]) {
                                /* set rubber */
                                match[loser + "_score"](1);
                                match.events().rubber(true);
                            }
                        }

                        /* end match */
                        match.in_progress(false);

                        /* push state to storage */
                        match.update();

                    } else {
                        /* match still in progress. get latest match data without updating */
                        match.get();
                    }

                }
            });
        }

        Entity.call(self, id, options);
    }
    Game.prototype = Object.create(Entity.prototype);


    Game.prototype.onAfterMap = function(json) {
        var self = this;
        self.ordinal = self.configuration.json.ordinal;
    };

    Game.prototype.get = function(callback) {
        var self = this;

        api.getGame(self.tourney.id, self.match.id, self.id,
            function(json) {
                self.map(json["game"]);
                self.configuration.json = json["game"]; //save raw data
                self.onAfterMap(json["game"]);
                if (typeof callback == "function") {
                    callback.call(self, json);
                }
            }
        );
    };

    Game.prototype.update = function(callback) {
        var self = this,
            data = {};

        data["game"] = mapping.toJS(self);

        api.updateGame(self.tourney.id, self.match.id, self.id, data,
            function(json) {
                if (typeof callback == "function") {
                    callback.call(self, json);
                }
            }
        );
    };

    Game.prototype.setWinner = function(team) {
        var self = this;
        // set winner id
        self.winner_id(self.match.tourney[team + "_team_id"]);

        //update game
        self.update(function(json) {
            // set in progress. This prompts Match to update, sets score. TODO: write match update
            self.in_progress(false);

            //self.match.get();
            /*
                we should probably wait until match gets updated to reload it. In fact, update match (all entities?) to update with server data on update. If we calculate match points on the controller this will eliminate the need to do an extra get to pull the match point info. 
            */
        });

        /* TODO

        Update match so that it subscribes to game.in_progress. when in_progress == false, match should check for:

         * is match over?
            * update match.winner_id
            * update "sweep" event
            * update match.in_progress
            * set match points (? or perhaps this should be done in the controller as part of before_http_action_callback call on match update ?)
         * "rubber" event?

         Tourney should, in turn, subscribe to match.in_progress. when in_progress == false then tourney should check for... tourney complete? maybe nothing?

         * create utility for determining match points. It's silly to have rulesets & scoring only on the server side. There's so much league specific stuff in this code.


        if (self.match[team + "_games_won"]++ >= self.match[team + "_games_needed"]) {
            self.match.in_progress(false);
            self.match.winner_id(self.match.tourney[team + "_team_id"]);
            self.match.update();
        }

        */
    };

    return entity;
});