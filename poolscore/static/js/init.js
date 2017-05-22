/* init.js */
// Main require.js init script 

require.config({
    // ***********************************************
    // Use this only in test mode
    // urlArgs: 'bust=' + (new Date()).getTime(),
    // ***********************************************

    baseUrl: '/static/js',

    shim: {
        bootstrap : {
            deps: ['jquery'],
            exports: 'Bootstrap'
        }
    },

    paths: {
        jquery:         'https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min',
        bootstrap:      'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/js/bootstrap.min',
        knockout:       'http://cdnjs.cloudflare.com/ajax/libs/knockout/3.1.0/knockout-min',

        libs:           'libs'
    }
});
