var Future = Npm.require("fibers/future");
var exec = Npm.require("child_process").exec;
var fs = Npm.require('fs');

var pwd = process.env.PWD;
var server_images = "/server/.images/";
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

var dataFile = function(){
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
		} catch (e){
			return false;
		}
	},
	'request_search': function(keyword, type){
		//this.unblock();

		var future = new Future();
		var cmd = "python3 -S " + pwd+server_path + "/client.py " + type + " " + keyword;

		exec(cmd, function(error, stdout, stderr){
			if(error){
				console.log('error: client mysql failed');
				future.return([[], 0, 0]);
			} else {
				if(stdout == null || stdout.length == 0)
					future.return([[], 0, 0.0]);
				else {
					var resultset = stdout.split(" ");
					var elapsed = resultset.shift();
					var nresults = resultset.shift();

					for(i = 0; i < resultset.length; i++){
						resultset[i] = '.images/' + resultset[i]

						if(routed[resultset[i]] != true){
							Router.route(resultset[i], dataFile, {where: 'server'});
							routed[resultset[i]] = true;
						}
					}

					future.return([resultset, nresults, elapsed]);
				}
			}
		});

		return future.wait();
	}
});

Meteor.startup(function(){
	/* Server folder of images */
	mkdirExists(pwd + server_images);
});
