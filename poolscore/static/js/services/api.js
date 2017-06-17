/* API service */

define(['jquery',
        'knockout'],
function($, ko) {

    'use strict';

    var root = "/api/v1.0/";

    function _path(path) {
        var i=1;
        if (path === undefined) return "";

        while(i < arguments.length) {
            path = path.replace(/%s/,arguments[i++]);
        }

        return root + path;
    }

    function _run(method, url, payload, callback) {
        var settings = {
                type: method,
                url: url,
                data: payload,
                dataType: "json"
            };

        if (method == undefined || url == undefined) return;

        if (typeof payload == 'object') {
            if ($.isEmptyObject(payload)) {
                settings.data = '';
            } else {
                settings.data = JSON.stringify(payload);
            }
        } else {
            settings.data = payload;
        }

        if (typeof callback == "function") {
            settings.success = callback;
        }

        return $.ajax(settings);
    }

    function _get(url, callback) {
        return _run("GET", url, "", callback)
    }

    function _put(url, payload, callback) {
        return _run("PUT", url, payload, callback)
    }

    function _post(url, payload, callback) {
        return _run("POST", url, payload, callback)
    }

    function _delete(url, callback) {
        return _run("DELETE", url, "", callback)
    }

    return {
        createTourney: function(data, callback) {
            var url = _path("tourneys.json");
            return _post(url, data, callback);
        },

        getTourneys: function(callback) {
            var url = _path("tourneys.json");
            return _get(url, callback);
        },

        getTourney: function(tourney_id, callback) {
            var url = _path("tourneys/%s.json", tourney_id);
            return _get(url, callback);
        },

        updateTourney: function(tourney_id, data, callback) {
            var url = _path("tourneys/%s.json", tourney_id);
            return _put(url, data, callback);
        },

        getMatches: function(tourney_id, callback) {
            var url = _path("tourneys/%s/matches.json", tourney_id);
            return _get(url, callback);
        },

        createMatch: function(tourney_id, data, callback) {
            var url = _path("tourneys/%s/matches.json", tourney_id);
            return _post(url, data, callback);
        },

        getMatch: function(tourney_id, match_id, callback) {
            var url = _path("tourneys/%s/matches/%s.json", tourney_id, match_id);
            return _get(url, callback);
        },

        updateMatch: function(tourney_id, match_id, data, callback) {
            var url = _path("tourneys/%s/matches/%s.json", tourney_id, match_id);
            return _put(url, data, callback);
        },

        getGames: function(tourney_id, match_id, callback) {
            var url = _path("tourneys/%s/match/%s/games.json", tourney_id, match_id);
            return _get(url, callback);
        },

        createGame: function(tourney_id, match_id, data, callback) {
            var url = _path("tourneys/%s/matches/%s/games.json", tourney_id, match_id);
            return _post(url, data, callback);
        },

        getGame: function(tourney_id, match_id, game_id, callback) {
            var url = _path("tourneys/%s/matches/%s/games/%s.json", tourney_id, match_id, game_id);
            return _get(url, callback);
        },

        updateGame: function(tourney_id, match_id, game_id, data, callback) {
            var url = _path("tourneys/%s/matches/%s/games/%s.json", tourney_id, match_id, game_id);
            return _put(url, data, callback);
        }
    }

});