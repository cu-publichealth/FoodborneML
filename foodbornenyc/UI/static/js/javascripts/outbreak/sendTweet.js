$(function() {
	$('.error').hide();
	$(".send-tweet-btn").click(function() {
		// validate and process form here
      
	$('.error').hide();
		var userHandle = $("input#userHandle").val();  	
  		var tweetMessage = $("input#tweetMessage").val();
  		if (tweetMessage == "") {
        	tweetMessage = "Hi " + userHandle + "! Please click this link and fill the survey for DOHMH."
      	}

    	var dataString = '{userHandle:'+ userHandle + ', tweetMessage:' + tweetMessage + '}';
  		//alert (dataString);return false;

		$.ajax({
            type: 'PUT',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function() {
                alert('Survey request tweet sent to user.');
                var html = self.getDocumentHtml(document, outbreak);
                grade.parents('.document-card').replaceWith(html);
                self.checkToShowFinal();
            },
            error: function() {
                alert('An error occurred, please check your connection and try again');
            }
        })
	});
});