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

        self.raw = {};

        self.date = ko.observable();
        self.winner_id = ko.observable();
        self.home_score = ko.observable();
        self.away_score = ko.observable();

        self.home_team = ko.observable();
        self.away_team = ko.observable();

        self.matches = ko.observableArray();;

        // self.events = {};

        api.getTourney(options.tourney_id, function(json) {
            console.log(json);
            self.raw = json["tourney"];

            self.date(self.raw.date);
            self.winner_id(self.raw.winner_id);
            self.home_score(self.raw.home_score || 0);
            self.away_score(self.raw.away_score || 0);

            self.home_team(self.raw.home_team);
            self.away_team(self.raw.away_team);

            self.matches(self.raw.matches);
        });

        api.getMatches(options.tourney_id, function(json) {
            console.log(json);
            self.matches(json["matches"]);
        });

    }


});