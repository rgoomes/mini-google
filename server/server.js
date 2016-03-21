var Future = Npm.require("fibers/future");
var exec = Npm.require("child_process").exec;
var fs = Npm.require('fs');

var pwd = process.env.PWD;
var public_images = "/public/images/";
var server_images = "/server/images/";
var server_path = "/server"

var max_images = 100;

var mkdirExists = function(dir){
	if(!fs.existsSync(dir))
		fs.mkdirSync(dir);
};

var sendFile = Meteor.bindEnvironment(function(img){
	var future = new Future();
	var cmd = "cp " + pwd+server_path+"/"+img + " " + pwd+public_images;
	exec(cmd, function(error, stdout, stderr){ future.return(0); });

	return future.wait();
});

Meteor.methods({
	'search_by_keyword': function(keyword){
		this.unblock();

		var t = Date.now();
		var future = new Future();
		var cmd = "find " + pwd+server_images + " -type f -printf 'images/%f\n'";

		exec(cmd, function(error, stdout, stderr){
			if(error) future.return([[], 0, 0]);

			var elapsed = (Date.now() - t) / 1000.0;
			var resultset = stdout.match(/[^\n]+/g);

			if(resultset == null)
				future.return([[], 0, elapsed]);
			else {
				resultset = resultset.slice(0, Math.min(max_images,resultset.length));

				for(i = 0; i < resultset.length; i++)
					sendFile(resultset[i]);

				future.return([resultset, resultset.length, elapsed]);
			}
		});

		return future.wait();
	},
	'search_by_image': function(path){
		this.unblock();
	}
});

Meteor.startup(function () {
	console.log('server running..');

	/* Folders of images */
	mkdirExists(pwd + public_images);
	mkdirExists(pwd + server_images);
});
