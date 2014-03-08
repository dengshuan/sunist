$(document).ready(function() {
    var id = setInterval(update, 1000);
    function update() {
	var data = $.getJSON('/update', function(data) {
	    var N = data['counts'];
	    var modules = data['module'];
	    // console.log(module);
	    for (var i = 0; i < N; i++){
		var module = modules[i];
		var name = module['name'];
		var address = module['address'];
		var D = module['D'];
		var io = module['io'];
		$io = $("label.hidden:contains("+name+")").siblings(".io");
		for (var j = 0; j < 8; j++){
		    if (D[j] == 2) {
			$io.eq(j).text(io[j]);
		    }
		    else {
			$io.eq(j).children("button").text(io[j]);
		    }
		};
		
	    };
	    
	});
    };

    $("#test").click(function(){
	clearInterval(id);
    });

    $(".control").click(function(){
	var io = $(this).text();
	var address = $(this).parent().siblings("label.hidden").eq(1).text();
	var D = $(this).parent().attr("name");
	var packed_data = {"io": io,
			   "address": address,
			   "D": D
			  };
	$.ajax({
	    type: "POST",
	    url: '/control',
	    contentType: "application/json",
	    data: JSON.stringify(packed_data),
	    dataType: "json"
	});
    });

});
