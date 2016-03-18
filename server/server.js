var Future = Npm.require("fibers/future");
var exec = Npm.require("child_process").exec;

Meteor.methods({
	'search_by_keyword': function(keyword){
		this.unblock();

		var future = new Future();
		var command = "cd " + keyword + ";ls";

		exec(command, function(error, stdout, stderr){
		    if(error)
				future.return([]);

		    future.return(stdout.match(/[^\n]+/g));
		});

		return future.wait();
	},
	'search_by_image': function(){

	}
});

Meteor.startup(function () {
	console.log('server running..');

});
