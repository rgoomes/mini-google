Session.setDefault('images', []);
Session.setDefault('time', 0.0);
Session.setDefault('size', 0);

var request = '';

var search = function(evt){
	if(evt.target.value && evt.target.value.length && evt.which === 13){
		Router.go('/results');

		Meteor.call('get_type', evt.target.value, function(err, res1){
			Meteor.call(!res1 ? 'search_by_keyword' : 'search_by_image', evt.target.value, function(err, res2){
				Session.set('images', res2[0]);
				Session.set('size', res2[1]);
				Session.set('time', res2[2]);
			});
		});

	}
};

/* Home template methods */
Template.home.rendered = function(){
	$('#home-search-bar').focus();
	$('#home-search-bar').select();
	$('#home-search-bar').on('drop', function(evt){
		evt.preventDefault();
	});
}

Template.home.events({
	'keypress #home-search-bar': function (evt, template){
		search(evt);
	}
});

/* Results template methods */
Template.results.rendered = function(){
	$('#results-search-bar').focus();
	$('#results-search-bar').select();
	$('#results-search-bar').val(request);
	$('#results-search-bar').on('drop', function(evt){
		evt.preventDefault();
	});
}

Template.results.helpers({
	get_imgs: function() { return Session.get('images'); },
	get_time: function() { return Session.get('time'); },
	get_size: function() { return Session.get('size'); }
});

Template.results.events({
	'keypress #results-search-bar': function (evt, template){
		search(evt);
	}
});

Router.route('/', function(){
	this.render('home');
});

Router.route('/results', function(){
	this.render('results');
});
