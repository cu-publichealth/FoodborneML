var restaurants;

var tweetsView = Backbone.View.extend({

	events: {
		//--- annotation events
		"click .edit-document-label": 				"editDocumentLabel",
		"click .save-document": 					"updateDocument",
		"change .labelSomeoneGotSick": 				"labelSickChanged",
		"click .cancel-edit-document": 				"cancelEditDocument",
		
		//--- message
		"click .twitter-message-card-read-more": 	"readMore",
		"click .twitter-message-card-read-less": 	"readLess",

		//--- surveys
		"click .show-surveys-expand": 				"showSurveys",
		"click .show-surveys-hide": 				"hideSurveys",
		"click .fill-in-survey": 					"fillInSurvey",
		"click .survey-submit": 					"surveySubmit",
		"click .survey_submit_cancel": 				"closeForms",

		//-- contact user
		"click .contact-user-document": 			"contactUser",
		"click .cancel-send-tweet-btn": 			"closeContactUser",
		"click .send-tweet-btn": 					"sendTweet",

		//-- link tweet
		"click .link-tweet-restaurant": 			"linkTweetForm",
		"click .link_restaurant_btn": 				"linkTweet",
		"click .link_restaurant_close_btn": 		"closeForms",

		//--- start investigation
		"click .start-investigation": 				"startInvestigation",
		"click .close_start_investigation_restaurant_select": "closeForms",


		//--- add tweet to investigation
		"click .add-to-investigation": 				"addToInvestigation",
		"click .add-to-outbreak": 					"addToOutbreak",
		"click .add_inv_close_btn": 				"closeForms",

		//--- show sent tweets
		"click .show-sent-tweets": 					"showSentTweets",

		//--- show timeline
		"click .show-timeline": 					"showTimeline",

		//--- linked restaurants 
		"click .linked-restaurants-show": 			"showRestaurants",
		"click .linked-restaurants-hide": 			"hideRestaurants"


	},


	initialize: function () {
		var self = this;
		self.twitter_messages = self.options.data;
		self.title = self.options.title;

		//EventManager.on('show-twitter-message', function (tweetId) {
		//	var twitter_message = _.find(self.twitter_mesages, function (twitter_message) {
		//		return twitter_mesagge.tweet_id === tweetId;
		//	});

			//if (twitter_message) {
			//	self.renderOutbreak(twitter_message);
			//}
			//else {
			//	self.$el.html('');
			//}
		//});

		//EventManager.on('show-cards', function() {
		//	self.renderTwitterMessageCards();
		//});
		self.renderTwitterMessageCards();
	},


	// ------------------------------------
	// ------------- RENDER ---------------
	// ------------------------------------
	renderTwitterMessageCards: function () {
		var self = this;
		//self.$el.mustache('twitter_messages', {title : self.id}, {method : 'html'});
		serial_id = 1;
		_.each(self.twitter_messages, function(twitter_message) {
			card = self.twitterMessageCardView(twitter_message);
			card.isEditMode = false;
			card.serial_id = serial_id++;
			result = $.Mustache.render('twitter-message-card', card);
			docCard = $(result);
			docCard.find('dt[data-toggle="tooltip"]').tooltip();
			$('.twitter-messages-wrapper').append(result);
		});
		self.$el.find('.twitter-messages-back').hide();
	},

	twitterMessageCardView: function (tw_msg, isEditMode) {
		var t =  tw_msg.text;
		var t_s = t.split(' ').slice(0,20).join(' ');
		function getMapUrl(lat, lon) {
			return 'https://www.google.com/maps/place/' + lat + ',' + lon;
		}
	   
		var locurl;
		if(tw_msg.latitude)
			locurl = getMapUrl(tw_msg.latitude, tw_msg.longitude);
		else 
			locurl = "#";

		return {
			id: 					tw_msg.doc_id,
			tweet_id: 				tw_msg.tweet_id,
			text: 					tw_msg.text,
			createdDate: 			moment(tw_msg.createdDate).format('MMM DD, YYYY - hh:mm a'),
			username: 				tw_msg.user.name,
			screenName: 			tw_msg.user.screenName,
			sick_score: 			parseFloat(tw_msg.sick_score).toFixed(3),
			dateCreated: 			moment(tw_msg.createdDate).format('MMM DD, YYYY - hh:mm a'),
			url: 					'https://twitter.com/' + tw_msg.user.screenName + '/status/' + tw_msg.tweet_id,
			userHandle: 			tw_msg.user.screenName,
			location: 				(tw_msg.latitude ? 'View on map' : null),
			locationUrl: 			locurl,
			userLocation: 			tw_msg.user.location,
			visitDate: 				moment(tw_msg.visitDate).format('MMM DD, YYYY - hh:mm a'),
			timesLabeled: 			'<b>' + tw_msg.label_info.times_labeled + '</b> annotations',
			timesLabeledF: 			(tw_msg.label_info.times_labeled==0 ? false : true),
			linkLabel: 				"YES",
			labelSomeoneGotSick: 	(tw_msg.label_info.someone_got_sick ?  tw_msg.label_info.someone_got_sick : "UNKNOWN"),
			labelSeriousEnough: 	(tw_msg.label_info.serious_enough ? tw_msg.label_info.serious_enough : "UNKNOWN"),
			labelTimingConsistent: 	(tw_msg.label_info.timing_consistent ? tw_msg.label_info.timing_consistent : "UNKNOWN"),
			labeledBy: 				(tw_msg.label_info.labeled_by_name ? tw_msg.label_info.labeled_by_name : "UNKNOWN"),
			labelNotes: 			(tw_msg.label_info.notes && tw_msg.label_info.notes.trim().length>0 ? tw_msg.label_info.notes : "NONE"),
			labeledDate: 			(moment(tw_msg.label_info.date).isAfter("1990-01-01T01:01:01Z") ? moment(tw_msg.label_info.date).format('MMM DD, YYYY - hh:mm a') : "NEVER"),
			labelNYCLocated: 		tw_msg.label_info.nyc_located,

			isPartOfInvestigation:  (tw_msg.partOfInvestigation == null ? false : (tw_msg.partOfInvestigation!=0)),
			partOfInvestigation:    (tw_msg.partOfInvestigation == null ? 0 	:  tw_msg.partOfInvestigation),
			hasCompletedSurveys: 	(tw_msg.completedSurveys == null 	? false : (tw_msg.completedSurveys!=0)),
			completedSurveys : 		(tw_msg.completedSurveys == null 	? 0 	:  tw_msg.completedSurveys),
			hasLinkedRestaurants: 	(tw_msg.linkedRestaurants== null 	? false : (tw_msg.linkedRestaurants!=0)),
			linkedRestaurants: 		(tw_msg.linkedRestaurants==null 	? 0 	:  tw_msg.linkedRestaurants),
			
			hasExpandedTimline: 	(tw_msg.timeline_expansion_attempted_date == null ? false : (moment(tw_msg.timeline_expansion_attempted_date).isAfter("1990-01-01T01:01:01Z") ? true : false)),
			hasTrackedConversation: (tw_msg.conversation_tracking_attempted_date == null ? false : (moment(tw_msg.conversation_tracking_attempted_date).isAfter("1990-01-01T01:01:01Z") ? true : false))
		};
	},

	getDocumentHtml: function (doc, outbreak, isEditMode) {
		var self = this;
		var result = null;
		if (doc.source === "TWITTER") {
			var card = self.makeTwitterMessageCard(doc.data);
			card = self.makeClassifiable(card, doc, outbreak, "YES");
			card.isEditMode = isEditMode || !card.labeledDate;
			result = $($.Mustache.render('twitter-message-card', card));
			self.setDocumentLabels(result, card);
		}
		return result;
	},

  
	// ------------------------------------
	// ------------- EVENTS ---------------
	// ------------------------------------
	readMore: function(e) {
		e.preventDefault();
		var tweetId = $(e.currentTarget).data('id');
		$('#text_small_'+tweetId).fadeOut();
		$('#text_large_'+tweetId).fadeIn();
	},

	readLess: function(e) {
		e.preventDefault();
		var tweetId = $(e.currentTarget).data('id');
		$('#text_large_'+tweetId).fadeOut();
		$('#text_small_'+tweetId).fadeIn();
	},

	// ------------------------------------
	// -------- GENERIC EVENTS ------------
	// ------------------------------------
	toggleTarget: function(e) {
		e.preventDefault();

		var clicked = $(e.currentTarget);

		var target = $(clicked.data('target'));

		if (target.is(':visible')) {
			target.slideUp();
		}
		else {
			target.slideDown();
		}
	},


	// ------------------------------------
	// ---------- UTILITIES ---------------
	// ------------------------------------
	getMapUrl: function(lat, lon) {
		return 'https://www.google.com/maps/place/' + lat + ',' + lon;
	},

	getUnknownMapUrl: function() {
		// alert('No location data is available for this business');
	},

	getMultiMapUrl: function(coordsWithColor) {
		var mapUrl = 'http://maps.google.com/maps/api/staticmap?size=640x640&sensor=false';

		var getMarker = function(color, lat, lon) {
			return '&markers=color:' + color + '|' + lat + ',' + lon;
		};

		_.each(coordsWithColor, function(c) {
			mapUrl += getMarker(c.color, c.coord[1], c.coord[0]);
		});

		return mapUrl;
	},

	errorHandler: function(msg) {
		noty({
			text: msg,
			layout: "topLeft",
			type: "error"
		});
		return;
	},

	successHandler: function(msg) {
		noty({
			text: msg,
			layout: "topLeft",
			type: "success"
		});
		return;
	},

	// ------------------------------------
	// ---------- ANNOTATIONS -------------
	// ------------------------------------
	labelSickChanged: function(e) {
		var clicked = $(e.currentTarget);

		var extra = clicked.parents('.document-grade').find('.extra-questions');

		if (clicked.val() === "YES") {
			extra.slideDown();
		}
		else {
			extra.slideUp();
		}
	},

	updateDocument: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var grade = button.parents('.document-grade');
		var documentCard = button.parents('.document-card');
		var serial_id = documentCard.find('.mserial_id').html();

		var document = {};
		document.docId  = documentId;
		document.labelSeriousEnough = grade.find('.labelSeriousEnough').val();
		document.labelSomeoneGotSick = grade.find('.labelSomeoneGotSick').val();
		document.labelTimingConsistent = grade.find('.labelTimingConsistent').val();
		document.linkLabel = 'UNKNOWN';
		document.notes = grade.find('.notes').val();
		document.labeledDate = moment(); /* moment will use the current time from the current locale. Instead we keep track of the date server-side */
		document.labelNYCLocated = grade.find('.labelNYCLocated').val();
		var data = _.pick(document, 'docId', 'labelSeriousEnough', 'labelSomeoneGotSick', 'labelTimingConsistent', 'linkLabel', 'notes', 'labelNYCLocated');
		

		$.ajax({
			type: 'PUT',
			data: JSON.stringify(data),
			contentType: 'application/json',
			url: '/api/detected_twitter/annotate/' + encodeURIComponent(documentId),
			success: function(apiResp) {
				console.log(apiResp.data);
				ccard  = self.twitterMessageCardView(apiResp.data);
				console.log(ccard);
				ccard.serial_id = serial_id
				ccard.isEditMode = false
				html = $.Mustache.render('twitter-message-card', ccard);
				grade.parents('.document-card').replaceWith(html);
			},
			error: function() {
				self.errorHandler('An error occurred, please check your connection and try again');
			}
		});
	},

	editDocumentLabel: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		var serial_id = documentCard.find('.mserial_id').html();

		//get latest snapshot of label
		$.ajax({
			async: false,
			url: '/api/detected_twitter/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					self.errorHandler('Failed to get up-to-date information for tweet with Complaint Id: '+ documentId +'.');
				yp = apiResp;
				card  = self.twitterMessageCardView(yp.data);
				card.serial_id = serial_id;
				card.isEditMode = true
				html = $.Mustache.render('twitter-message-card', card)
				button.parents('.document-card').replaceWith(html);
			},
			error: function(data) {
				self.errorHandler('Failed to get up-to-date information for tweet with Complaint Id: '+ documentId +'.');
			}
		});
	},

	cancelEditDocument: function(e){
		e.preventDefault();
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		var serial_id = documentCard.find('.mserial_id').html();

		//get latest snapshot of label
		$.ajax({
			async: false,
			url: '/api/detected_twitter/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					self.errorHandler('Failed to get up-to-date information for tweet with Complaint Id: '+ documentId +'.');
				yp = apiResp;
				card  = self.twitterMessageCardView(yp.data);
				card.serial_id = serial_id
				html = $.Mustache.render('twitter-message-card', card)
				button.parents('.document-card').replaceWith(html);
			},
			error: function(data) {
				self.errorHandler('Failed to get up-to-date information for tweet with Complaint Id: '+ documentId +'.');
			}
		});
	},

	contactUser: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		$("#contact_user_"+documentId).show();
	},

	closeContactUser: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		$("#contact_user_" + documentId).hide();
	},

	linkTweet: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');

		var form = button.parents('#link_restaurant_form');

		var data = {};
		form.serializeArray().map(function(x){data[x.name] = x.value;});

		data.restaurantId = form.find("#restaurantId").val();
		data.linkedTweetDocumentId = documentId;

		$.ajax({
			type: "PUT",
			contentType: "application/json",
			url: '/api/detected_twitter/link/' + documentId,
			dataType: 'json',
			data: JSON.stringify(data),
			success: function(apiResp) {
				if (apiResp && apiResp.success){
					$("#linked_restaurants_"  + documentId).show();

					documentCard.find(".linked-restaurants-hide").show();
					documentCard.find(".linked-restaurants-show").html('Show ' + apiResp.data.length + " linked restaurants.");
					documentCard.find(".linked-restaurants-show").hide();
					html = "";
					res = apiResp.data;
					for(i = 0; i < res.length; ++i){
						html += res[i].bview.name  + "<br/>";
					}
					$("#linked_restaurants_list_"+documentId).html(html);
					console.log('linked');
				}else
					return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant ' + apiResp.error);
			},
			error: function(data) {
				return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant ' + apiResp.error);
			}
		});
	},

	linkTweetForm: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		tid = {id: documentId}
		html = $.Mustache.render('link-restaurant-card', tid);
		card = $(html);

		$("#restaurantNameOnlineD").css('display', 'inline');
		card.find("#restaurantName").val('');
		card.find("#restaurantAddress").val('');
		card.find("#restaurantId").val('');
		card.find("#linkedTweetDocumentId").val(documentId);

		card.find('.form-horizontal').prepend($("#restaurantNameOnlineD"));

		//add to DOM
		var linkForm = documentCard.find('.link_restaurant_row');
		linkForm.html(card.html());
		
		//add typeahead event listeners
		self.makeTypeahead('restaurantNameOnline');

		//show form
		linkForm.show();
	},

	showRestaurants: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		res = [];
		$.ajax({
			async: false,
			url: '/api/detected_twitter/linked_restaurants/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (apiResp && apiResp.success)
				{
					res = apiResp.data;
					html = "";
					for(i = 0; i < res.length; ++i){
						html += res[i].bview.name  + "<br/>";
					}
					documentCard.find(".linked-restaurants-show").hide();
					documentCard.find(".linked-restaurants-hide").show();
					$("#linked_restaurants_list_"+documentId).html(html);
				}else{
					return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant ' + apiResp.error);
				}
			},
			error: function(data) {
				return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant ' + apiResp.error);
			}
		});
	},

	hideRestaurants: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		documentCard.find(".linked-restaurants-show").show();
		documentCard.find(".linked-restaurants-hide").hide();
		$("#linked_restaurants_list_"+documentId).html('');
	},

	showSentTweets: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
	},

	makeSurveyView: function(obj){
		function getMapUrl(lat, lon) {
			return 'https://www.google.com/maps/place/' + lat + ',' + lon;
		}

		var locurl;
		if(obj.business.location.latitude)
			locurl = getMapUrl(obj.business.location.latitude, obj.business.location.longitude);
		else 
			locurl = "#";

		return {
			//user
			userId: obj.user.uid,
			userName: obj.user.first_name + "," + obj.user.last_name,
			userEmail: obj.user.email,
			userPhone: obj.user.phone,

			//survey
			surveyId: obj.survey.id,
			incidentDescription: obj.survey.incidentDescription,
			incidentDate: moment(obj.survey.incidentDate).format('MMM DD, YYYY'),
			createdDate: moment(obj.survey.createdDate).format('MMM DD, YYYY'),

			//business
			businessName: obj.business.name,
			businessUrl: obj.business.business_url,
			businessPhone: obj.business.phone,
			businessRating: obj.business.rating,
			businessLocation: obj.business.location.line_1 + "," + obj.business.location.city + "," + obj.business.location.postal_code,
			businessLocationUrl: locurl
		}
	},

	showSurveys: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');

		$.ajax({
			async: false,
			url: '/api/detected_twitter/fetch_surveys/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					self.errorHandler('Failed to get surveys for tweet with Complaint Id: '+ documentId +'.');
				
				documentCard.find(".show-surveys-expand").html('Show ' + apiResp.data.length + " surveys.");

				documentCard.find(".show-surveys-expand").hide();
				documentCard.find(".show-surveys-hide").show();
				documentCard.find(".surveys_display_row").html('');
				documentCard.find("#completed_surveys_"+documentId).show();
				for(i = 0; i < apiResp.data.length; ++i){
					survey = self.makeSurveyView(apiResp.data[i]);
					html = $.Mustache.render('filled-in-survey-card', survey);
					documentCard.find(".surveys_display_row").append(html);
				}
			},
			error: function(data) {
				self.errorHandler('Failed to get surveys for tweet with Complaint Id: '+ documentId +'.');
			}
		});
	},

	hideSurveys: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		documentCard.find(".show-surveys-expand").show();
		documentCard.find(".show-surveys-hide").hide();
		documentCard.find(".surveys_display_row").html('');
	},

	fillInSurvey: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		tid = {id: documentId}
		html = $.Mustache.render('survey-card', tid);
		card = $(html);

		$("#restaurantNameOnlineD").css('display', 'inline');
		card.find('.form-horizontal').prepend($("#restaurantNameOnlineD"));
		
		var survey = documentCard.find('.survey_row');
		survey.html(card.html());
		survey.show();

		self.makeTypeahead('restaurantNameOnline');

		$('#survey_'+documentId).bootstrapValidator({
			live: 'submitted',
			fields: {
				restaurantName: {
					validators: {
						notEmpty: {
							message: 'Restaurant name is required'
						}
					}
				},
				restaurantAddress: {
					validators: {
						notEmpty: {
							message: 'Restaurant address is required'
						}
					}
				},
				incidentDescription: {
					validators: {
						notEmpty: {
							message: 'Incident description is required'
						}
					}
				},
				incidentDate: {
					validators: {
						notEmpty: {
							message: 'Incident date is required'
						},
						date: {
							format: 'YYYY-MM-DD',
							message: 'This is not a valid date (e.g. 11/28/2013)'
						}
					}
				},
				userFirstName: {
					validators: {
						notEmpty: {
							message: 'First name is required'
						}
					}
				},
				userLastName: {
					validators: {
						notEmpty: {
							message: 'Last name is required'
						}
					}
				},
				userEmail: {
					validators: {
						notEmpty: {
							message: 'Email address is required'
						},
						emailAddress: {
							message: 'This is not a valid email address'
						}
					}
				},
				userPhone: {
					validators: {
						phone: {
							message: 'This is not a valid phone number'
						}
					}
				}
			},
			submitHandler: function(validator, form, submitButton) {
				// get post data from form
				var data = {};
				form.serializeArray().map(function(x){data[x.name] = x.value;});

				data.restaurantId = restaurantId;
				data.tweetId = tweetId;

				var errorHandler = function(msg) {
					noty({
						text: msg,
						layout: "topLeft",
						type: "error"
					});
					return;
				};

				var infoHandler = function(msg) {
					noty({
						text: msg,
						layout: "top",
						type: "information"
					});
					return;
				};

				$.ajax({
					type: "PUT",
					url: "/api/detected_twitter/fill_in_survey/" + documentId,
					contentType: "application/json",
					dataType: "json",
					data: JSON.stringify(data),
					success: function(apiResp) {
						console.log(apiResp)
						if (!apiResp || apiResp.success==false) {
							return errorHandler('Failed to submit survey: ' + apiResp.error);
						}
						infoHandler('Survey submitted successfully');
						self.clearForms(documentId, documentCard);
						//show surveys
						documentCard.find(".show-surveys-expand").trigger('click');
					},
					error: function(err) {
						errorHandler('Failed to submit survey. Application appears to be down completely. Contact the admin');
					}
				});
			}
		});
	},

/*
	NOT AVAILABLE IN v1.0
	showTimeline: function(e){
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		$.ajax({
			async: false,
			url: '/api/detected_twitter/show_timeline/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					self.errorHandler('Failed to get tweets for tweet with Complaint Id: '+ documentId +'.');
				documentCard.find(".show-timeline-section").html('');
				html = "<ul class=\"timeline\">";
				for(i = 0; i < apiResp.data.length; ++i){
					tweet = self.makeTweetCard(apiResp.data[i]); 
					html += "<li>"  + $.Mustache.render('show-timeline-card', timeline) + "</li>";
				}
				html += "</ul>";
				documentCard.find(".show-timeline-section").append(html);
			},
			error: function(data) {
				self.errorHandler('Failed to get surveys for tweet with Complaint Id: '+ documentId +'.');
			}
		});
	},
*/
	clearForms: function(documentId, documentCard){
		$("#contact_user_" + documentId).hide();
		var self = this;
		$('.survey_row').html('');
		$('.survey_row').hide();

		$('.link_restaurant_row').html('');
		$('.link_restaurant_row').hide();

		$('.add-to-investigation-row').html('');
		$('.add-to-investigation-row').hide();
	},

	makeTypeahead: function(id){
		$("#" + id).typeahead({
			source: restaurants.data,
			minLength: 2,
			items: 100,
			matcher: function(item) {
				var toMatch = item.name + ' ' + item.fullAddress;
				var queryParts = this.query.toLowerCase().split(' ');
				return _.every(queryParts, function(part) {
					return toMatch.toLowerCase().indexOf(part) != -1;
				});
			},
			sorter: function(items) {
				var beginswith = []
					, caseSensitive = []
					, caseInsensitive = []
					, item;
				while (item = items.shift()) {
					if (!item.name.toLowerCase().indexOf(this.query.toLowerCase())) {
						beginswith.push(item);
					}
					else if (~item.name.indexOf(this.query)) {
						caseSensitive.push(item);
					}
					else {
						caseInsensitive.push(item);
					}
				}

				return beginswith.concat(caseSensitive, caseInsensitive)
			},
			highlighter: function(item) {
				return $.Mustache.render('biz-highlight', item);
			},
			updater: function(item) {
				restaurantId = item.id;
				$('#restaurantAddress').val(item.fullAddress);
				$('#restaurantId').val(item.id);
				return item.name;
			}
		}).focus();
	},

	makeInvTable: function(card, tbl, documentId){
		var inv_dtbl = $("#inv_table").DataTable({
			responsive: false,
			columns: [
				{"data" : "restaurant"},
				{"data" : "date_created"},

				{"data" : "yelp"},
				{"data" : "twitter"},
				{"data" : "nyc311"},

				{"data" : "inv_id"},
				
				{"data" : "status"},
				{"data" : "action"},
				{"data" : "start"},
				{"data" : "end"},
				{"data" : "created_by"},

				{"data" : "actions"},
				
			],
			"order": [[1, "desc"]],
			"aoColumnDefs": [
				{
					"bSortable": false,
					"aTargets": 
					[
						11
					]
				},
				{
					"type": 'date',
					"aTargets": 
					[
						2, 9, 10
					]
				},
			],
			"fnRowCallback": function(nRow, aData, iDisplayIndex){
				$('td', nRow).eq(0).attr('nowrap', 'nowrap');
				$('td', nRow).css('padding', '0 0 0 0');
				$('td', nRow).css('margin', '0 0 0 0');
				for(idx = 0; idx < 11; ++idx)
						$('td', nRow).eq(idx).css('background-color', '#FCFCFA');
				$('td', nRow).css('font-weight', 'bolder');
				$('td', nRow).css('text-align', 'center');
				$('td', nRow).eq(11).css('text-align', 'left');
				$('td', nRow).eq(11).css('background-color', 'brown');
				$('td', nRow).eq(11).css('color', 'white');
				$('td', nRow).eq(0).css('text-align', 'left');
				return nRow;
			},
			"fnHeaderCallback": function( thead, data, start, end, display ) {
				$(thead).find('th').each(function(){
					$(this).css('background-color','#404040');
					$(this).css('color','white');
					$(this).css('font-weight','bolder');
					$(this).css('text-align','center');
				});
			},
			"drawCallback": function( settings ) {
	        	$("#inv_table").wrap( "<div class='table-responsive'></div>" );
	        }
		});

		function getMapUrl(lat, lon) {
			return 'https://www.google.com/maps/place/' + lat + ',' + lon;
		}
			
		//fill it in
		for(i = 0; i < tbl.length; ++i){
			r = [];

			//make restaurantName
			if(tbl[i].restaurantUrl)
				restaurantName = ("<a href=\"" + tbl[i].restaurantUrl + "\" style=\"font-size: 24px;\">" + tbl[i].restaurantName + "</a>");
			else
				restaurantName = tbl[i].restaurantName;

			var locUrl;
			if(tbl[i].loc_latitude)
				locUrl = this.getMapUrl(tbl[i].loc_latitude,  tbl[i].loc_longitude);
			else 
				locUrl = "#";

			restaurantAddress='';
			if(tbl[i].address){
				restaurantAddress = tbl[i].address;
			}

			if(!(locUrl==='#') && !(restaurantAddress===''))
				restaurantAddress =  ("<a href=\"" + locUrl+ "\">" + restaurantAddress + "</a>");

			if(restaurantAddress!=='')
				restaurantName = restaurantName + "<br/>" + restaurantAddress;

			r["inv_id"] = "<b>"+tbl[i].investigation_id+"</b>";
			r["restaurant"] = restaurantName,
			r["status"] = "<span id=\"status-"+tbl[i].investigation_id+"\">"+tbl[i].inv_status+"</span>";
			r["action"] = tbl[i].action;
			r["start"] = (tbl[i].inv_start == null ? "NEVER" : (moment(tbl[i].inv_start).isAfter("1990-01-01T01:01:01Z") ? moment(tbl[i].inv_start).format('MM/DD/YYYY hh:mm') : "NEVER"));
			r["end"] = (tbl[i].inv_end == null ? "NEVER" : (moment(tbl[i].inv_end).isAfter("1990-01-01T01:01:01Z") ? moment(tbl[i].inv_end).format('MM/DD/YYYY hh:mm') : "NEVER"));
			r["date_created"] = (tbl[i].out_created == null ? "NEVER" : (moment(tbl[i].out_created).isAfter("1990-01-01T01:01:01Z") ? moment(tbl[i].out_created).format('MM/DD/YYYY hh:mm') : "NEVER"));
			r["yelp"] = tbl[i].yelp;
			r["twitter"] = tbl[i].twitter;
			r["nyc311"] = tbl[i].nyc311;
			r["created_by"] = tbl[i].createdBy;
			
			r["actions"] = "<div id=\"actions-"+tbl[i].investigation_id+"\">&#8658;" 
						+ "<a href=\"#\" class=\"add_inv\" data-id=\""+tbl[i].investigation_id+"\" data-oid=\""+tbl[i].outbreak_id+"\" data-tid=\""+documentId+"\" style=\"color:white\">Add</a></div>";
			inv_dtbl.row.add(r).draw();
		}
		return card;
	},

	addToInvestigation: function(e){
		e.preventDefault();
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		var tid = {id: documentId}
		html = $.Mustache.render('add-to-investigation-card', tid);
		card = $(html);
		
		
		$.ajax({
			url: '/api/investigations',
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					return errorHandler('Failed to get investigations.');
				else if (!apiResp.success)
					return errorHandler('Failed to get investigations: ' + apiResp.error);
				var investigations = documentCard.find('.add-to-investigation-row');
				investigations.show();
				investigations.html(card.html());
				card = self.makeInvTable(card, apiResp.data, documentId)
				
				$("#inv_table").on('click', '.add_inv', function(e){
					self.addInv(e);
				});
			},
			error: function(data) {
				errorHandler("Failed to get outbreaks. The application appears to be down completely.");
			}
		});
	},

	addInv: function(e){
		self = this;
		e.preventDefault();
		inv = $(e.currentTarget);
		iid = inv.data('id');
		oid = inv.data('oid');
		tid = inv.data('tid');
		var documentCard = inv.parents('.document-card');

		$.ajax({
			url: '/api/investigations/add/' + iid + "?document_id=" + urlEncode(tid) + "&outbreak_id=" + urlEncode(oid) ,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					return self.errorHandler('Failed to add to investigation.');
				else if (!apiResp.success)
					return self.errorHandler('Failed to add to investigation: ' + apiResp.error);
				console.log(apiResp);
				if(apiResp.data === 0)
					self.successHandler('Complaint-Tweet ' + tid +' is already part of investigation ' + iid);
				else{
					self.successHandler('Complaint-Tweet ' + tid +' was successfully added to investigation ' + iid);
					documentCard.find(".partof-inv").html(parseInt(documentCard.find(".partof-inv").html())+1);
				}
				self.clearForms();
				
				documentCard.find("#partof_inv_"+tid).show();
				
			},
			error: function(data) {
				self.errorHandler("Failed to add complaint " + tid + ". The application appears to be down completely.");
			}
		});
	},


	startInvestigation: function(e){
		e.preventDefault();
		e.preventDefault();
		var self = this;
		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);

		//getLinkedRestaurants
		res = [];
		$.ajax({
			async: false,
			url: '/api/detected_twitter/linked_restaurants/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (apiResp && apiResp.success)
					res = apiResp.data;
				else
					return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant ' + apiResp.error);
				console.log(res);
			},
			error: function(data) {
				return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant ' + apiResp.error);
			}
		});
		
		//ask
		if(res.length == 0 )
			return self.errorHandler('Failed to get restaurants for the particular tweet! Please consider first linking the tweet to a restaurant');
		else if(res.length==1){
			rid = res[0].bview.id;
		}else{
			for(i = 0; i < res.length; ++i)
			{
				html += "<option value=\""+res[i].bview.id+"\">"+res[i].name+"</option>";
			}
			tid = {id: documentId}
			html = $.Mustache.render('start-investigation-card', tid);
			card = $(html);

			card.find("#start_investigation_select").html(html);
			var startInv = documentCard.find('.start-investigation-row');
			startInv.html(card.html());
			startInv.show();
			return;
		}

		//start investigation
		console.log(documentId);
		$.ajax({
			url: '/api/investigations/start/' + documentId + '?business_id=' + urlEncode(rid),
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					return self.errorHandler('Failed to get investigations.');
				else if (!apiResp.success)
					return self.errorHandler('Failed to get investigations: ' + apiResp.error);
				self.successHandler('New investigation ' + apiResp.data + " just got created!");
			},
			error: function(data) {
				console.log(JSON.stringify(data));
				self.errorHandler("Failed to add complaint " + tid + ". The application appears to be down completely.");
			}
		});
	},

	closeForms: function(e){
		e.preventDefault();
		var self = this;
		button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);
	}
});