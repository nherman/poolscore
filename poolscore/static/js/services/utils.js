define(['jquery',
        'knockout'],
function($, ko) {

    'use strict';

    return {
        isEmpty: _isempty
    };

    function _isempty(v) {
        return (v == undefined || v == null || v == "");
    }

});