(function($){
	$(document).ready(function(){
		var selected_tags = new Array()

		// get tags for event
		var pathname = location.pathname;
		if(pathname.indexOf('/events/edit') > -1){
			$.get('/events/view/' + $('input[name=id]').val(), function(data){
				$(data.tags).each(function(){
					selected_tags.push( { id : this.tag_id, name : this.name, reference : this.reference } );
				});
				updateSelectedTags(selected_tags);
			});
		}

		// add tag to event

		$('.add_tag').click(function(e){
			e.preventDefault()
			tag_data = {tag : $('.tag-autocomplete').val()};
			console.log(tag_data);
			$.ajax({
				type: "POST",
				contentType: "application/json; charset=utf-8",
				url: "/tags/add/",
				data: JSON.stringify(tag_data),
				success: function (data) {
					selected_tags.push(data);
					updateSelectedTags(selected_tags);
					console.log(selected_tags);
					$(this).val('');
					return false;
				},
				dataType: "json"
			});
		});

		// tag auto complete
		$.get('/tags/', function(data){
			var tags = new Array()
			for(var i = 0; data.Tags.length > i; i++){
				tags.push({index : i, label : data.Tags[i]['Tag']['name'], value : data.Tags[i]['Tag']['id']})
			}
			$('.tag-autocomplete').autocomplete({
				source: tags,
				select: function( event, ui ){
					selected_tags.push(data.Tags[ui.item.index]);
					updateSelectedTags(selected_tags);
					$(this).val('');
					return false;
				}
			});
		});

		// add / edit event

		$('.edit-event').submit(function(e){
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
		//	location.reload();
		});

		$('.add-event').submit(function(e){
			e.preventDefault();
			var form_json = $(this).serializeArray();
			form_json.push({'tags' : selected_tags});
			$.ajax({
				type: "POST",
				contentType: "application/json; charset=utf-8",
				url: "/events/add/",
				data: JSON.stringify(form_json),
				dataType: "json"
			});
//			location.reload();
		});


		function updateSelectedTags(selected_tags){
			$('ul.tags').empty();
			$(selected_tags).each(function(){
				var tagList = $('<li />').text(this.name).attr('data-tagid', this.id);
				tagList.click(removeTag);
				$('ul.tags').append(tagList)
			});
		}
		function removeTag(){
			var tag = this;
			$(selected_tags).each(function(index){
				if(this.id == $(tag).attr('data-tagid')){
					selected_tags.splice(index, 1);
				}
			})
			updateSelectedTags(selected_tags);
		}

	});
})(jQuery);
