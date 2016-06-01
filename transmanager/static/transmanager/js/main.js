$(document).ready(function(){

    // Para los selects
    $('select').chosen({});
    $('body').on('click', 'li.tab-pane > a', function(e){
        $('.chosen-container').css('width', '100%');
        e.preventDefault();
    });

    // reset form
    $('body').on('click', '.reset-filters', function(e){
        e.preventDefault();
        $(this).closest('form').
            find("input[type=text]").val("").end().
            find("select").val('').trigger('liszt:updated').end().
            submit();
    });

});