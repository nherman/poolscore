/* main.js */

define('pages/main', ['knockout', 'pages/tourney'], function(ko, tourneyViewModel) {


    function mainViewModel() {
        var self = this;

        self.mainComponent = ko.observable({
            'name':'tourney-component',
            'params': {
                'id':1
            }
        });

    }

    return mainViewModel;

});