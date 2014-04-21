(function($){
	$(document).ready(function(){
		var selected_tags = new Array()
		
		// get tags for event
		$.get('/events/view/' + $('input[name=id]').val(), function(data){
			$(data.tags).each(function(){
				selected_tags.push(this);
				updateSelectedTags(selected_tags);
			});
		});
		
		// add tag to event
		
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
		
		// add / edit event
		
		$('.add-event, .edit-event').submit(function(e){
			e.preventDefault();
			var form_json = $(this).serializeArray();
			form_json.push({'tags' : selected_tags});
			$.ajax({
				type: "POST",
				contentType: "application/json; charset=utf-8",
				url: "/events/edit/",
				data: JSON.stringify(form_json),
				dataType: "json"
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