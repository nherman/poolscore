/* tourney.js */

define('components/tourney', ['knockout'], function(ko) {

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

        self.tourney_id = options.tourney_id;
        self.home_team_id = "";
        self.away_team_id = "";
        self.home_team = {};
        self.away_team = {};


        self.date = ko.observable();
        self.winner_id = ko.observable();
        self.home_score = ko.observable();
        self.away_score = ko.observable();
        self.matches = ko.observableArray();

        self.events = {};

    }


});