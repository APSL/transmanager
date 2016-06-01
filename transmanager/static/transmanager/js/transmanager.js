/**
 * Class that handles
 * @constructor
 */
TransManager = function(){
    this.api_url = $('#transmanager-api-menu').data('api-url');
    this.app_label = $('#transmanager-api-menu').data('app-label');
    this.model = $('#transmanager-api-menu').data('model');
    this.ids = [$('#transmanager-api-menu').data('pk')];
    this.id_menu_button ='#btn-transmanager-api-menu';
    this.id_menu_button_remove ='#btn-transmanager-api-menu-remove';
    this.langs = [];
};
TransManager.prototype.getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
TransManager.prototype.sendPost = function(){
    var self=this;
    self.langs = [];
    $('#transmanager-api-menu #more-languages input:checked').each(function(index){
        self.langs.push($(this).val());
    });
    var data = {app_label: self.app_label, model: self.model, ids: self.ids, languages: self.langs};
    $.post(this.api_url, JSON.stringify(data), function(result){
        alert('Generadas las peticiones de traducción para el elemento');
        window.location.reload();
    }, 'json').fail(function(result){
        alert('Error: '+result.responseText);
    });
};
TransManager.prototype.sendDelete = function(){
    var self=this;
    self.langs = [];
    $('#transmanager-api-menu #item-languages input:checked').each(function(index){
        self.langs.push($(this).val());
    });
    var data = {app_label: self.app_label, model: self.model, ids: self.ids, languages: self.langs};
    $.ajax({
        url: self.api_url,
        method: 'delete',
        data: JSON.stringify(data),
        success: function(result) {
            alert('Eliminadas las peticiones de traducción pendientes para el elemento');
            window.location.reload();
        },
        fail: function(result){
            alert('Error: '+result.responseText);
        }
    });
};
TransManager.prototype.init = function(){
    var self=this;
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", self.getCookie('csrftoken'));
            xhr.setRequestHeader("Content-Type", 'application/json');
        }
    });
    $('body').on('click', self.id_menu_button, function(){
        self.sendPost();
    });
    $('body').on('click', self.id_menu_button_remove, function(){
        self.sendDelete();
    });
    $('#transmanager-api-menu .dropdown-menu input, .dropdown-menu label').click(function(e) {
        e.stopPropagation();
    });
};

window.onload = function(){
    var man = new TransManager();
    man.init();
};
