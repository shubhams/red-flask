$('.search_url').on('click', function(){
	$('.processing_div').show();
	$('.error_div').hide()
	$('.result_div').hide();

	input_url = $('#url').val()
	$.ajax({
		url: '/search_url',
		data: {
			format: 'json',
			url: input_url
		},
		error: function() {
			$('.processing_div').hide();
			$('.error_div').show()
		},
		success: function(data) {
		    console.log(data)
			$('.processing_div').hide();
			if (data['status'] == true){
			    $('#num_views').html(data['num_views'])
			    $('#num_comments').html(data['num_comments'])
			    $('#num_dislikes').html(data['num_dislikes'])
			    $('#num_favourites').html(data['num_favourites'])
			    $('#num_channel_videos').html(data['num_channel_videos'])
			    $('#num_channel_subscribers').html(data['num_channel_subscribers'])
			    $('#actual_likes').html(data['actual_likes'])
			    $('#predicted_likes').html(data['predicted_likes'])
				$('.result_div').show();
			}else {
				$('.error_div').show()
			}

		},
		type: 'POST'
	});

});

$(document).ready(function(){

});