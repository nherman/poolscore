/* tourney.js */

define('components/tourney', ['knockout'], function(ko) {

    'use strict';

    ko.components.register('tourney-component', {
        viewModel: tourneyViewModel,
        template: { require: 'text!partials/tourney.html' }
    });

    return tourneyViewModel;

    function tourneyViewModel(options) {
        var self = this,
            _options = ko.utils.extend({
                "tourney_id": ""
            }, options);

        if (_options.tourney_id === undefined || _options.tourney_id === "") {
            throw "Invalid Tourney ID"
        }

        self.id = _options.tourney_id;
        console.log(_options);

    }


});