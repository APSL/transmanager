/**
 * Translated list manager
 * @constructor
 */
Translated = function(){

};
Translated.prototype.init = function(){
    $('input[id^="id_dates_"]').datepicker({
        language: 'es',
        format: 'yyyy-mm-dd'
    }).addClass('datepicker');
};
$(document).ready(function(){
    var trans = new Translated();
    trans.init();
});
