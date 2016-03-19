var Future = Npm.require("fibers/future");
var exec = Npm.require("child_process").exec;

Meteor.methods({
	'search_by_keyword': function(keyword){
		this.unblock();

		var t = Date.now();
		var future = new Future();
		var command = "cd " + keyword + ";ls";

		exec(command, function(error, stdout, stderr){
			var resultset = stdout.match(/[^\n]+/g);
			var elapsed = (Date.now() - t) / 1000.0;

			if(resultset == null)
				future.return([[], 0, elapsed]);
			else
				future.return([resultset, resultset.length, elapsed]);
		});

		return future.wait();
	},
	'search_by_image': function(){

	}
});

Meteor.startup(function () {
	console.log('server running..');

});
