(function($){
	$(document).ready(function(){
		// var json = {
		// 		name : 'Great Fire of London',
		// 		date_from : '1666-09-02',
		// 		date_to :  '1666-09-05',
		// 		link : 'http://en.wikipedia.org/wiki/Great_Fire_of_London'
		// 	}

		$.ajax({
			type: 'POST',
			url: '/events/edit/',
			dataType: 'json',
			contentType: 'application/json',
			data: JSON.stringify(json)
		});
	});
})(jQuery);
