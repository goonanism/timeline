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
					updateSelectedTags(selected_tags);
				},
				dataType: "json"
			});
		});
		
		
		// tag auto complete
		$.get('/tags/', function(data){
			var tags = new Array()
			for(var i = 0; data.tags.length > i; i++){
				tags.push({index : i, label : data.tags[i].name, value : data.tags[i].id})
			}
			$('.tag-autocomplete').autocomplete({
				source: tags,
				select: function( event, ui ){
					selected_tags.push(data.tags[ui.item.index]);
					updateSelectedTags(selected_tags);
				}
			});
		});
		
		function updateSelectedTags(selected_tags){
			$('ul.tags').empty();
			$(selected_tags).each(function(){
				var tagList = $('<li />').text(this.name).attr('data-tagid', this.id);
				$('ul.tags').append(tagList)
			});
		}
		
	});
})(jQuery);