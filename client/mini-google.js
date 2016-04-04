Session.setDefault('images', []);
Session.setDefault('time', 0.0);
Session.setDefault('size', 0);

var request = '';

var search = function(evt, page){
	if(evt.target.value && evt.target.value.length && evt.which === 13){
		if(page == "home")
			Session.set('images', []);

		request = evt.target.value;
		Router.go('/results');

		Meteor.call('get_type', request, function(err, res1){
			type = !res1 ? 'keyword' : 'image';
			Meteor.call('request_search', request, type, function(err, res2){
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
		search(evt, "home");
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
		search(evt, "results");
	}
});

Router.route('/', function(){
	this.render('home');
});

Router.route('/results', function(){
	this.render('results');
});
