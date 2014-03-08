$(document).ready(function(){
    function fillContents(){
	var data = $.getJSON('/update', function(data) {
	    var counts = data['counts'];
	    var module = data['module'];
	    for (var i = 0; i < counts; i++) {
		var panel = '<div id="panel' + module[i]['id'] + '" class="panel panel-primary"><div class="panel-heading"><h3 class="panel-title"><a href="#module' + module[i]['id'] + '"data-toggle="collapse" data-parent="#accordion">'+ module[i]['name'] + '</a></h3></div></div>';
		$(".jumbotron").append(panel);
		var detail = '<div id="module' + module[i]['id'] + '" class="panel-body"></div>';
		$("#panel"+module[i]['id']).append(detail);
		var monitor = '<div class="monitor"><label>Monitor</label><br/></div>';
		var control = '<div class="control"><label>Control</label><br/></div>';
		$("#module"+module[i]['id']).append(monitor);
		$("#module"+module[i]['id']).append(control);

		var io = module[i]['io'];
		var D = module[i]['D'];
		for (var k = 0; k < 8; k++) {
		    if (D[k] == 2) { // monitor ADC
			var $io = '<span class="port"><label>' + k + ':</label><span class="value">' + io[k] + '</span></span>';
			$("#module"+module[i]['id']).children(".monitor").append($io);
		    }
		    else if (D[k] == 3) { // monitor DI
			if (io[k] == true) {
			var $io = '<span class="port"><label>' + k + ':</label>' + '<input type="checkbox" checked disabled class="switch"></span>';
			}
			else {
			    var $io = '<span class="port"><label>' + k + ':</label>' + '<input type="checkbox" disabled class="switch"></span>';
			}
			$("#module"+module[i]['id']).children(".monitor").append($io);			
		    }
		    else if (D[k] == 4) { // control DO low
			var $io = '<span class="port"><label>' + k + ':</label>' + '<input type="checkbox" class="switch"></span>';
			$("#module"+module[i]['id']).children(".control").append($io);
		    }
		    else if (D[k] == 5) { // control DO high
			var $io = '<span class="port"><label>' + k + ':</label>' + '<input type="checkbox" checked class="switch"></span>';
			$("#module"+module[i]['id']).children(".control").append($io);
		    }
		};

	    };

	    $(".switch").bootstrapSwitch();	    
	});
    };
    fillContents();


    function update() {
	$.getJSON('/update', function(data) {
	    var counts = data['counts'];
	    var module = data['module'];
	    for (var i = 0; i < counts; i++) {
		var io = module[i]['io'];
		var D = module[i]['D'];
		for (var j = 0; j < 8; j++) {
		    // var $mod = $(".panel:contains('" + module[i]['name'] + "') label:contains(" + D[j] ")");

		};
	    }
	});
    };
    // setInterval("update()",1000);

    $(".switch").on('switch-change', function(e, data) {
	var value = $(this).bootstrapSwitch('state');
	var port = $(this);
	var cmd = {
	    "name": "module-0",
	    "port": 3,
	    "value": data.value
	};
	$.post("/control", cmd, "json");
    });

});
