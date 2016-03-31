var Future = Npm.require("fibers/future");
var exec = Npm.require("child_process").exec;
var fs = Npm.require('fs');

var pwd = process.env.PWD;
var server_images = "/server/images/";
var server_path = "/server"

var max_images = 100;
var routed = {};

var mkdirExists = function(dir){
	if(!fs.existsSync(dir))
		fs.mkdirSync(dir);
};

var fail = function(response){
	response.statusCode = 404;
	response.end();
};

var dataFile = function() {
	var file = pwd + server_path + this.url;
	var stat = null;

	try {
		stat = fs.statSync(file);
	} catch (_error) {
		return fail(this.response);
	}

	this.response.writeHead(200, {
		'Content-Type': 'application/jpeg',
		'Content-Disposition': 'attachment;',
		'Content-Length': stat.size
	});

	fs.createReadStream(file).pipe(this.response);
};

Meteor.methods({
	'get_type': function(value){
		try {
			return fs.statSync(value).isFile();
		} catch (e){ return false; }
	},
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

				for(i = 0; i < resultset.length; i++){
					if(routed[resultset[i]] != true){
						Router.route('/' + resultset[i], dataFile, {where: 'server'});
						routed[resultset[i]] = true;
					}
				}

				future.return([resultset, resultset.length, elapsed]);
			}
		});

		return future.wait();
	},
	'search_by_image': function(path){
		this.unblock();
		return [[], 0, 0.0];
	}
});

Meteor.startup(function () {
	console.log('server running..');

	/* Server folder of images */
	mkdirExists(pwd + server_images);
});
