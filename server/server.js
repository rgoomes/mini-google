var Future = Npm.require("fibers/future");
var exec = Npm.require("child_process").exec;
var fs = Npm.require('fs');

var pwd = process.env.PWD;
var spark_path = "/server/.spark-1.6.0-bin-hadoop2.6/";
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

var startSparkServer = function() {
	var cmd = "python3 " + pwd+server_path + "/server_spark.py --save --path " + pwd+server_path;

	exec(cmd, function(error, stdout, stderr){
		if(error)
			console.log('error: failed to start spark');
	});
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
		this.unblock();

		var t = Date.now();
		var future = new Future();
		var cmd = "python3 -S " + pwd+server_path + "/client_spark.py " + type + " " + keyword;

		exec(cmd, function(error, stdout, stderr){
			var elapsed = (Date.now() - t) / 1000.0;

			if(error){
				console.log('error: client spark failed');
				future.return([[], 0, 0]);
			} else {
				if(stdout == null || stdout.length == 0)
					future.return([[], 0, elapsed]);
				else {
					var resultset = stdout.split(" ");
					var setlength = resultset.length;
					resultset = resultset.slice(0, Math.min(max_images, setlength));

					for(i = 0; i < resultset.length; i++){
						resultset[i] = '.images/' + resultset[i]

						if(routed[resultset[i]] != true){
							Router.route(resultset[i], dataFile, {where: 'server'});
							routed[resultset[i]] = true;
						}
					}

					future.return([resultset, setlength, elapsed]);
				}
			}
		});

		return future.wait();
	}
});

Meteor.startup(function(){
	/* Spark folder */
	if(!fs.existsSync(pwd + spark_path)){
		console.log('error: spark not found');
		//process.exit(0);
	} else
		startSparkServer()

	/* Server folder of images */
	mkdirExists(pwd + server_images);
});
