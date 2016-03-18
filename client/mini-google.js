Session.setDefault('page', 'home');
Session.setDefault('images', []);

var search = function(evt, template, type /* by keyword or by image */ ){
    if(evt.which === 13 /* return keyevent value */ ){
        var keyword = evt.target.value;

        if(keyword.length){
            Session.set('page', 'results');
            Meteor.call('search_by_keyword', keyword, function(err, res){
                Session.set('images', res);
            })
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
        search(evt, template, 0);
    }
});

/* Results template methods */

Template.results.rendered = function(){
    $('#results-search-bar').focus();
    $('#results-search-bar').select();
}

Template.results.helpers({
    get_results: function () {
        return Session.get('images');
    }
});

Template.results.events({
    'keypress #results-search-bar': function (evt, template){
        search(evt, template, 0);
    }
});
