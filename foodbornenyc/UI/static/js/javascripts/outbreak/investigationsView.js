var InvestigationView = Backbone.View.extend({

	events: {
		"click .outbreak-card": 			"showOutbreak",
		"click .outbreak-card-positive": 	"showOutbreak",
		"click .outbreak-card-negative": 	"showOutbreak",        
		"click .outbreak-back": 			"showOutbreakCards",
		"click .save-outbreak": 			"updateOutbreak",
		"click .edit-outbreak-label": 		"editOutbreakLabel",
		"click .save-document": 			"updateDocument",
		"click .edit-document-label": 		"editDocumentLabel",
		"click .tweetSetToggle": 			"toggleTarget",
		"click .send-tweet-btn": 			"sendTweet",
		
		"change .labelSomeoneGotSick": 		"labelSickChanged"
	},

	initialize: function () {
		var self = this;
		self.investigation = self.options.data;
		self.title = self.options.title;
		self.renderOutbreak(self.investigation);
		$("html, body").animate({ scrollTop: $(".outbreaks").position().top }, "slow");
	},

	
	makeDate: function(date){
		return date ? 
		(
			moment(date).isAfter('1900-01-02 00:00:00') 
			? moment(date).format('MMM DD, YYYY') : 'NEVER'
		) : 'NEVER';
	},

	outbreakCardView: function (outbreak, isEditMode) {
		var self = this;
		var countBySource = _.countBy(outbreak.documents, 'source');
		var restaurant = outbreak.restaurant;

		//make investigation status
		var s=outbreak.investigation.status;
		if(s==='UNKNOWN')
			invstatus = '<span class="label label-warning" style="color: black;">NOT INITIATED</span>';
		else if(s===null)
			invstatus = '<span class="label label-warning" style="color: black;">UNDEFINED</span>';
		else
			invstatus = '<span class="label label-warning" style="color: black;">UNDEFINED</span>';

		//make restaurantName
		if(restaurant.url)
			restaurantLink = ("<a href=\"" + restaurant.url + "\">" + restaurant.name + "</a>");
		else
			restaurantLink = restaurant.name;

		return {
			id: outbreak.id,
			startDate: self.makeDate(outbreak.startDate), // .format('MMM DD, hh:mm a'),
			endDate: self.makeDate(outbreak.endDate),
			restaurantId: restaurant.id,
			restaurantLink: restaurantLink,
			restaurantName: restaurant.name,
			location: restaurant.location,
			url: restaurant.url,
			businessUrl: restaurant.businessUrl,
			categories: _.pluck(restaurant.categories, 'title').join(', '),
			yelpCount: outbreak.countYelp || 0,
			threeOneOneCount: outbreak.count311 || 0,
			twitterCount: outbreak.countTwitter || 0,
			isEditMode: isEditMode || outbreak.labeledDate === null,
			label: outbreak.label,
			labelNotes: outbreak.labelNotes,
			labeledDate : self.makeDate(outbreak.labeledDate),
			investigationId: outbreak.investigation.id===null ? "NO" : outbreak.investigation.id,
			investigationStatus: invstatus,
			investigationActiveDate: self.makeDate(outbreak.investigation.start),
			investigationClosedDate: self.makeDate(outbreak.investigation.end)
		};
	},


	renderOutbreak: function (outbreak, isEditMode) {
		var self = this;
		self.$el.mustache('outbreaks', {title : outbreak.restaurant.name}, {method : 'html'});
		self.$el.find('.outbreak-back').show();
		self.$el.find('.outbreak-wrapper').mustache('outbreak', self.outbreakCardView(outbreak, isEditMode), {method:'html'});
		self.$el.find('.outbreak-label').val(outbreak.label || "UNKNOWN");
		//now for each document, append to the right area
		_.each(outbreak.documents, function (doc) {
			self.renderDocument(doc, outbreak);
		});
	},

	renderDocument: function (doc, outbreak) {
		var self = this;
		var html = self.getDocumentHtml(doc, outbreak);
		console.log(html)
		if (doc.source === "YELP")
			self.$('.yelp-wrapper').append(html);
		else if (doc.source === "TWITTER")
			self.$('.twitter-wrapper').append(html);
		else if (doc.source === "NYC_311")
			self.$('.complaint-wrapper').append(html);
	},

	getDocumentHtml: function (doc, outbreak, isEditMode) {
		var self = this;
		var result = null;

		if (doc.source === "YELP") {
			var card = self.makeYelpCard(doc.data);
			card = self.makeClassifiable(card, doc, outbreak, "YES");
			card.isEditMode = isEditMode || !card.labeledDate;
			result = $($.Mustache.render('yelp-card', card));
			self.setDocumentLabels(result, card);
		}
		else if (doc.source === "TWITTER") {
			var card = self.makeTwitterCard(doc.data);
			card = self.makeClassifiable(card, doc, outbreak);
			card.isEditMode = isEditMode || !card.labeledDate;
			result = $($.Mustache.render('twitter-card', card));
			self.setDocumentLabels(result, card);
		}
		else if (doc.source === "NYC_311") {
			var card = self.makeComplaintCard(doc.data);
			card = self.makeClassifiable(card, doc, outbreak);
			card.isEditMode = isEditMode || !card.labeledDate;
			result = $($.Mustache.render('complaint-card', card));
			self.setDocumentLabels(result, card);
		}
		else {
			console.log("Unrecognized source!");
		}

		return result;
	},

	makeClassifiable: function(card, doc, outbreak, defaultLinkLabel) {
		
		defaultLinkLabel = defaultLinkLabel || "UNKNOWN";
		card.documentId = doc.id;
		card.labeledBy = doc.labeledBy;
		card.labeledDate = (doc.labeledDate ? (moment(doc.labeledDate).isAfter('1900-01-01 00:00') ? moment(doc.labeledDate).format('MMM DD, YYYY') : 'NEVER') : 'NEVER');
		card.labelSeriousEnough = doc.labelSeriousEnough || "UNKNOWN";
		card.labelSomeoneGotSick = doc.labelSomeoneGotSick || "UNKNOWN";
		card.labelTimingConsistent = doc.labelTimingConsistent || "UNKNOWN";
		card.linkLabel = doc.linkLabel || defaultLinkLabel;
		card.linkLabelNotes = doc.linkLabelNotes;

		card.restaurantName = outbreak.restaurant.name;
		card.startDate = moment(outbreak.startDate).format('MMM Do, YY');
		card.endDate = moment(outbreak.endDate).format('MMM Do, YY');

		return card;
	},

	setDocumentLabels: function(docCard, card) {
		
		docCard.find(".linkLabel").val(card.linkLabel);
		docCard.find(".labelSomeoneGotSick").val(card.labelSomeoneGotSick);
		docCard.find(".labelTimingConsistent").val(card.labelTimingConsistent);
		docCard.find(".labelSeriousEnough").val(card.labelSeriousEnough);
		if (card.labelSomeoneGotSick === "YES") {
			docCard.find(".extra-questions").show();
		}
		docCard.find('dt[data-toggle="tooltip"]').tooltip();
	},

	makeYelpCard: function(data) {
		
		return {
			date: moment(data.createdDate).format('MMM DD, YYYY'),
			rating: data.rating,
			text: data.text,
			userName: data.userName,
			url: data.url
		};
	},

	makeTwitterCard: function(data) {
		var self = this;
		var tweet = self.makeSingleTweetCard(data.tweet);
		tweet.expandedTweetSet = _.map(data.expandedTweetSet, function(t) {
			return self.makeSingleTweetCard(t);
		});
		tweet.hasExpandedTweetSet = tweet.expandedTweetSet.length > 0;
		return tweet;
	},

	makeSingleTweetCard: function(tweet) {
		self = this;
		return {
			id: tweet.id,
			date: moment(tweet.createdDate).format('MMM DD, YYYY - hh:mm a'),
			text: tweet.text,
			userHandle: tweet.user.screenName,
			location: tweet.latitude ? 'View on map' : null,
			locationUrl: tweet.latitude ? self.getMapUrl(tweet.latitude, tweet.longitude) : self.getUnknownMapUrl(),
			url: 'https://twitter.com/' + tweet.user.screenName + '/status/' + tweet.id,
			hasExpandedTweetSet: false
		};
	},

	makeComplaintCard: function(data) {
		return {
			details: data.details,
			address: data.streetAddress + ', ' + data.city + ' ' + data.zipCode,
			date: moment(data.incidentDate).format('MMM DD, YYYY - hh:mm a'),
			siteName: data.siteName,
			id: data.id
		};
	},

	// ------------------------------------
	// ------------- EVENTS ---------------
	// ------------------------------------

	showOutbreak: function(e) {
		e.preventDefault();
		var outbreakId = $(e.currentTarget).data('id');
		EventManager.trigger('show-outbreak', outbreakId);
	},

	showOutbreakCards: function(e) {
		e.preventDefault();
		EventManager.trigger('show-cards');
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

	updateOutbreak: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var labelNotes = button.siblings('.notes').first().val();
		var label = button.parent().find('.outbreak-label').val();

		var outbreakId = self.$('.outbreak').data('id');

		data = {
			id: outbreakId,
			label: label,
			labelNotes: labelNotes
		}; 

		$("#loader").fadeIn(300);
		$.ajax({
			type: 'PUT',
			data: JSON.stringify(data),
			contentType: 'application/json',
			dataType: 'json',
			url: '/api/outbreak/label/' + outbreakId,
			success: function(apiResp) {
				$("#loader").fadeOut(300);
				if (!apiResp || apiResp.sucess==false)
					return self.errorHandler('Failed to update outbreak.');
				self.renderOutbreak(apiResp.data, false);
			},
			error: function(result) {
				$("#loader").fadeOut(300);
				return self.errorHandler("Failed to update outbreak. The application appears to be down completely.");
			}
		});
	},

	updateDocument: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var grade = button.parent();

		var outbreakId = grade.parents('.outbreak').data('id');

		var tempOutbreak;

		$.ajax({
			async: false,
			url: '/api/outbreak/outbreak/' + outbreakId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp || !apiResp.success)
					return self.errorHandler('Failed to get outbreak. Please contact admin' + (apiResp ? ": " + apiResp.error + "." : "!"));
				tempOutbreak = apiResp.data;
			},
			error: function(data) {
				return self.errorHandler("Failed to get outbreak. The application appears to be down completely.");
			}
		});
		outbreak = tempOutbreak;

		var document = _.find(outbreak.documents, function(doc) {
			return doc.id == documentId;
		});

		document.labelSeriousEnough = grade.find('.labelSeriousEnough').val();
		document.labelSomeoneGotSick = grade.find('.labelSomeoneGotSick').val();
		document.labelTimingConsistent = grade.find('.labelTimingConsistent').val();
		document.linkLabel = grade.find('.linkLabel').val();
		document.linkLabelNotes = grade.find('.notes').val();
		document.labeledDate = moment();
		
		var data = _.pick(document, 'source', 'labelSeriousEnough', 'labelSomeoneGotSick', 'labelTimingConsistent', 'linkLabel', 'linkLabelNotes');
		$.ajax({
			type: 'PUT',
			data: JSON.stringify(data),
			contentType: 'application/json',
			url: '/api/outbreak/document/' + documentId + "?oid=" + outbreakId,
			success: function() {
				var html = self.getDocumentHtml(document, outbreak);
				grade.parents('.document-card').replaceWith(html);
			},
			error: function() {
				return self.errorHandler("Failed to get outbreak. The application appears to be down completely.");
			}
		});
	},

	editOutbreakLabel: function(e) {
		console.log("In editOutbreakLabel");
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var outbreakId = button.data('id');

		var outbreak = _.find(self.outbreaks, function(outbreak) {
			return outbreak.id == outbreakId;
		});

		console.log(outbreakId);
		$("#loader").fadeIn(300);

		$.ajax({
			url: '/api/outbreak/outbreak/' + outbreakId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp || !apiResp.success) {
					self.errorHandler('Failed to get outbreak. Please contact admin' + (apiResp ? ": " + apiResp.error + "." : "!"));
					$("#loader").fadeIn(300);
				}
				$("#loader").fadeOut(300);
				self.renderOutbreak(apiResp.data, true);
			},
			error: function(data) {
				$("#loader").fadeIn(300);
				errorHandler("Failed to get outbreaks. The application appears to be down completely.");
			}
		});
	},

	sendTweet: function(e) {
		e.preventDefault();
		var self = this;
		
		var tweetMessage = $("input#tweetMessage").val();
		var tweetId = $("input#tweetId").val();

		console.log(tweetMessage);
		console.log(tweetId);

		if (tweetMessage == "") {
			alert('Please enter a message to send to the user.');
			return;
		}

		var userHandle = tweetMessage.split(' ')[1];
		userHandle = userHandle.substr(1, userHandle.length-2);

		var dataString = '{"DOHMHtweet": {"userHandle": \"'+ userHandle + '\", "tweetMessage": \"' + tweetMessage + '\", "tweetId": \"' + tweetId + '\"}}';
		console.log(dataString);

		$.ajax({
			type: 'PUT',
			data: dataString,
			contentType: 'application/json',
			url: '/api/outbreak/sendTweet/' + userHandle,
			success: function() {
				alert('Survey request tweet sent to user.');
			},
			error: function() {
				alert('An error occurred, please check your connection and try again');
			}
		})
	},
	
	editDocumentLabel: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');

		var outbreakId = button.parents('.outbreak').data('id');

		var outbreak = _.find(self.outbreaks, function(outbreak) {
			return outbreak.id == outbreakId;
		});

		var tempOutbreak;
		$.ajax({
			async: false,
			url: '/api/outbreak/outbreak/' + outbreakId,
			dataType: 'json',
			success: function(apiResp) {

				if (!apiResp) {
					alert('Failed to get outbreak.');
				}
				tempOutbreak = apiResp.data;
			},
			error: function(data) {
				errorHandler("Failed to get outbreaks. The application appears to be down completely.");
			}
		});
		outbreak = tempOutbreak;

		var document = _.find(outbreak.documents, function(doc) {
			return doc.id == documentId;
		});

		var html = self.getDocumentHtml(document, outbreak, true);
		button.parents('.document-card').replaceWith(html);
	},

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
		//alert('No location data is available for this business');
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
	}

});