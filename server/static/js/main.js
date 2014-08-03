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
