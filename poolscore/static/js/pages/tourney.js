/* tourney.js */

define('pages/tourney', ['knockout'], function(ko) {

    ko.components.register('tourney-component', {
        viewModel: tourneyViewModel,
        template: { require: 'text!partials/pirates.html' }
    });

    function tourneyViewModel(params) {
        var self = this;

        self.id = params.id;

    }

    return tourneyViewModel;

});