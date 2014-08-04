$(window).on('touchmove', function(e) { e.preventDefault(); });

$(function() {
	var canvas = $('canvas#canvas');
	if(canvas.length == 1) {
		var context = canvas[0].getContext("2d");
		var drawing = false;
		var pos;
		function get_pos(event) {
			var mouseX = event.pageX - canvas.offset().left;
			var mouseY = event.pageY - canvas.offset().top;
			return {x:mouseX, y:mouseY};
		}
		function get_tablet_pos() {
			var mouseX = event.changedTouches[0].pageX - canvas.offset().left;
			var mouseY = event.changedTouches[0].pageY - canvas.offset().top;
			return {x:mouseX, y:mouseY};
		}
		context.strokeStyle = '#000';
		context.lineWidth = 5;
		context.lineJoin = "round";
		context.lineCap = "round";
		canvas.on({
			'mousedown': function(e) {
				drawing = true;
				pos = get_pos(e);
			},
			'touchstart': function(e) {
				drawing = true;
				pos = get_tablet_pos(e);
			},
			'mousemove': function(e) {
				var current_pos = get_pos(e);
				if(drawing) {
					context.beginPath();
					context.moveTo(pos.x, pos.y);
					context.lineTo(current_pos.x, current_pos.y);
					context.stroke();
					context.closePath();
					pos = current_pos;
				}
			},
			'touchmove': function(e) {
				var current_pos = get_tablet_pos();
				if(drawing) {
					context.beginPath();
					context.moveTo(pos.x, pos.y);
					context.lineTo(current_pos.x, current_pos.y);
					context.stroke();
					context.closePath();
					pos = current_pos;
				}
			},
			'mouseup': function() { drawing = false; },
			'mouseleave': function() { drawing = false; },
			'touchend': function() { drawing = false; }
		});

		$("#delete_button").click(function () {
			context.clearRect(0, 0, canvas.width(), canvas.height());
		});
	}
});

$(function() {
	var p = $('#progress');
	p.progressbar({
		value: 0,
		change:
		function() {
			$('#loading').text(p.progressbar('value') + '%');
		},
		complete:
		function() {
			//window.alert('complete');
		}
	});

	var id = setInterval(function() {
		var v = p.progressbar('value');
		p.progressbar('value', ++v);
		if (v >= 100) { clearInterval(id) }
	}, 100);
});
