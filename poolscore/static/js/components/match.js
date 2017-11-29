/* tourney.js */

define('components/match', ['knockout'], function(ko) {

    'use strict';

    ko.components.register('match-component', {
        viewModel: matchViewModel,
        template: { require: 'text!partials/match.html' }
    });

    return matchViewModel;

    function matchViewModel(options) {
        var self = this,
            _options = ko.utils.extend({
                "match_id": ""
            }, options);

        if (_options.match_id === undefined || _options.match_id === "") {
            throw "Invalid Match ID"
        }

        self.id = _options.match_id;
        console.log(_options);

    }


});