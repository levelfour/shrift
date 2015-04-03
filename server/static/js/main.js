$(window).on('touchmove', function(e) { e.preventDefault(); });

function set_pencil(context) {
	context.strokeStyle = '#000';
	context.lineWidth = 10;
	context.lineJoin = "round";
	context.lineCap = "round";
}

function set_eraser(context) {
	context.strokeStyle = '#fff';
	context.lineWidth = 50;
	context.lineJoin = "round";
	context.lineCap = "round";
}

function clear(context, canvas) {
	context.fillStyle = 'rgb(255,255,255)';
	context.fillRect(0, 0, canvas.width()+1, canvas.height()+1);
}

function send_image(canvas, url, filename) {
	var base64 = canvas[0].toDataURL('image/jpeg');
	var bin = atob(base64.split(',')[1]);
	var buffer = new Uint8Array(bin.length);
	for (var i = 0; i < bin.length; i++) {
		buffer[i] = bin.charCodeAt(i);
	}
	var file = new Blob([buffer.buffer], { type: 'image/jpeg' });
	var data = new FormData();
	data.append('file', file, filename+'.jpg');
	data.append('text', filename);
	$.ajax({
		type: 'POST',
		url: url,
		data: data,
		cache: false,
		processData: false,
		contentType: false,
		success: function(data) {
			alert(data);
		}
	});
}

$(function() {
	var canvas = $('canvas#canvas');
	if(canvas.length == 1) {
		var context = canvas[0].getContext("2d");
		
		if(canvas.attr('retina')) {
			var size = {w: canvas.width(), h: canvas.height()};
			canvas.css({
				'width': '95%',
				'height': '830px'
			});
			context.scale(size.w/canvas.width(), size.h/canvas.height());
		}
		
		var drawing = false;
		var erasing = false;
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
		clear(context, canvas);
		set_pencil(context);
		canvas.on({
			'mousedown': function(e) {
				drawing = true;
				pos = get_pos(e);
				$('#shrift').addClass('transparent');
				if($('#erase').css('opacity') == 1) {
					erasing = true;
				}
				if(erasing) {
					$('#eraser').css({
						display: 'block',
						top: pos.y,
						left: pos.x
					});
				}
			},
			'touchstart': function(e) {
				drawing = true;
				pos = get_tablet_pos(e);
				$('#shrift').addClass('transparent');
				if($('#erase').css('opacity') == 1) {
					erasing = true;
				}
				if(erasing) {
					$('#eraser').css({
						display: 'block',
						top: pos.y,
						left: pos.x
					});
				}
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
				if(erasing) {
					$('#eraser').css({
						top: current_pos.y,
						left: current_pos.x
					});
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
				if(erasing) {
					$('#eraser').css({
						top: current_pos.y,
						left: current_pos.x
					});
				}
			},
			'mouseup touchend': function() {
				drawing = false;
				setTimeout(function () {
					if(!drawing) {
						$('#shrift').removeClass('transparent');
					}
				}, 500);
				if(erasing) {
					$('#eraser').css('display', 'none');
				}
				if($('#erase').css('opacity') == 1) {
					erasing = false;
				}
			}
		});

		$('#send').on('click', function() {
			send_image(canvas, '/upload', $('#text').val());
			clear(context, canvas);
			return false;
		});
		
		$('#save').on('click', function() {
			if(confirm('Are you sure to save image?')) {
				window.location = canvas[0].toDataURL('image/jpeg');
			}
			return false;
		});
		
		$('#pen').on('touchend mouseup', function() {
			set_pencil(context);
			$('#pen').css('opacity', '1');
			$('#erase').css('opacity', '0.3');
			return false;
		});
		
		$('#erase').on('touchend mouseup', function() {
			set_eraser(context);
			$('#pen').css('opacity', '0.3');
			$('#erase').css('opacity', '1');
			return false;
		});
		
		$('#delete').on('touchend mouseup', function() {
			if(confirm('Are you sure to clear canvas?')) {
				clear(context, canvas);
			}
			return false;
		});

		$('#clear').on('touchend mouseup', function() {
			clear(context, canvas);
			return false;
		});
		
		$('#shrift').on('touchend mouseup', function() {
			$(this).addClass('hover');
			send_image(canvas, '/ocr', 'shrift');
			return false;
		});

		$('#shrift').removeClass('transparent');
	}
});

$(function() {
	$('a.delete-img').on('click', function() {
		if(confirm('Are you sure to delete data?')) {
			var url = "/delete/" + $(this).attr('data-target');
			$.ajax({
				type: 'GET',
				url: url,
				cache: false,
				processData: false,
				contentType: false,
				success: function(data) {
				}
			});
			$(this).remove();
		}
		return false;
	});
});

/*
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
*/
