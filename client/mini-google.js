Session.setDefault('page', 'home');
Session.setDefault('images', []);
Session.setDefault('time', 0.0);
Session.setDefault('size', 0);

var request = '';

var search = function(evt, template, type /* by keyword 1, or by image 0 */ ){
    if(evt.which === 13 /* return keyevent value */ ){
        var keyword = evt.target.value;
        request = type ? keyword : '';

        if(keyword.length){
            Session.set('page', 'results');
            Meteor.call('search_by_keyword', keyword, function(err, res){
                Session.set('images', res[0]);
                Session.set('size', res[1]);
                Session.set('time', res[2]);
            });
        }
    }
};

Template.body.helpers({
    route: function(){
        return Session.get('page');
    }
});

/* Home template methods */

Template.home.rendered = function(){
    $('#home-search-bar').focus();
    $('#home-search-bar').select();
}

Template.home.helpers({
});

Template.home.events({
    'keypress #home-search-bar': function (evt, template){
        search(evt, template, 1);
    }
});

/* Results template methods */

Template.results.rendered = function(){
    $('#results-search-bar').focus();
    $('#results-search-bar').select();
    $('#results-search-bar').val(request);
}

Template.results.helpers({
    get_imgs: function() { return Session.get('images'); },
    get_time: function() { return Session.get('time'); },
    get_size: function() { return Session.get('size'); }
});

Template.results.events({
    'keypress #results-search-bar': function (evt, template){
        search(evt, template, 1);
    }
});
