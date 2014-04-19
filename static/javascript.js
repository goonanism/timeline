(function($){
	$(document).ready(function(){
		var selected_tags = new Array()
		$('.add_tag').click(function(e){
			e.preventDefault()
			tag_data = {tag : $('input[name=tag]').val()};
			$.ajax({
				type: "POST",
				contentType: "application/json; charset=utf-8",
				url: "/tags/add/",
				data: JSON.stringify(tag_data),
				success: function (data) {
					selected_tags.push(data);
				},
				dataType: "json"
			});
		});
	});
})(jQuery);