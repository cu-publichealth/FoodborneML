var yelpReviewsView = Backbone.View.extend({
	events: {
		"click .yelp-review-card-read-more": 	"readMore",
		"click .yelp-review-card-read-less": 	"readLess",
		
		"click .edit-document-label": 			"editDocumentLabel",
		"click .save-document": 				"updateDocument",
		"change .labelSomeoneGotSick": 			"labelSickChanged",
		"click .cancel-edit-document": 			"cancelEditDocument",

		//start investigation
		//--- start investigation
		"click .start-investigation": 				"startInvestigation",
		"click .close_start_investigation_restaurant_select": "closeForms",

		//add to investigation
		//--- add tweet to investigation
		"click .add-to-investigation": 				"addToInvestigation",
		"click .add-to-outbreak": 					"addToOutbreak",
		"click .add_inv_close_btn": 				"closeForms"
	

	},

	initialize: function () {
		var self = this;
		self.yelp_reviews = self.options.data;
		self.title = self.options.title;

/*
		EventManager.on('show-yelp-review', function (yelpReviewId) {
			var yelp_review = _.find(self.yelp_reviews, function (yelp_review) {
				return yelp_review.id === yelpReviewId;
			});
			if (yelp_review) {
				self.renderOutbreak(yelp_review);
			}
			else {
				self.$el.html('');
			}
		});

		EventManager.on('show-cards', function() {
			self.renderYelpReviewCards();
		});
		*/
		self.renderYelpReviewCards();
	},


	// ------------------------------------
	// ------------- RENDER ---------------
	// ------------------------------------
	renderYelpReviewCards: function () {
		var self = this;

		serial_id = 1;
		_.each(self.yelp_reviews, function(yelp_review) {
			card = self.yelpCardView(yelp_review);
			//card.isEditMode = isEditMode || !card.labeledDate;
			card.serial_id = serial_id++;
			result = $.Mustache.render('yelp-review-card', card)
			docCard = $(result);
			docCard.find('dt[data-toggle="tooltip"]').tooltip();
			$(".yelp-reviews-wrapper").append(result);
		});

		self.$el.find('.yelp-review-back').hide();
	  //  self.$el.find('.yelp-reviews-wrapper').html(cardsHtml);
	},

	yelpCardView: function (yelp_review, isEditMode) {
		JSON.stringify(yelp_review)
		var t = yelp_review.text;
		var t_s = t.split(' ').slice(0,20).join(' ');
		function getMapUrl(lat, lon) {
			return 'https://www.google.com/maps/place/' + lat + ',' + lon;
		}

		var locurl;
		if(yelp_review.latitude)
			locurl = getMapUrl(yelp_review.latitude, yelp_review.longitude);
		else 
			locurl = "#";

		return {
			id: yelp_review.id,
			documentId: yelp_review.id,
			text: yelp_review.text,
			text_small: yelp_review.text.split(' ').slice(0,20).join(' '),
			text_large: yelp_review.text,
			createdDate: moment(yelp_review.createdDate).format('MMM DD, YYYY - hh:mm a'),
			rating: yelp_review.rating,
			url: yelp_review.url,
			userName: yelp_review.userName,
			businessId: yelp_review.business_id,
			businessName: yelp_review.business_name,
			businessUrl: yelp_review.business_url,
			location: yelp_review.address + ", " + yelp_review.city + ", " + yelp_review.postal_code,
			locationUrl: locurl,
			sick_score: parseFloat(yelp_review.sick_score).toFixed(3),
			dateCreated: moment(yelp_review.createdDate).format('MMM DD, YYYY - hh:mm a'),
			timesLabeled: '<b>' + yelp_review.label_info.times_labeled + '</b> annotations',
			timesLabeledF: (yelp_review.label_info.times_labeled==0 ? false : true),
			linkLabel: "YES",
			labelSomeoneGotSick: (yelp_review.label_info.someone_got_sick ?  yelp_review.label_info.someone_got_sick : "UNKNOWN"),
			labelSeriousEnough: (yelp_review.label_info.serious_enough ? yelp_review.label_info.serious_enough : "UNKNOWN"),
			labelTimingConsistent: (yelp_review.label_info.timing_consistent ? yelp_review.label_info.timing_consistent : "UNKNOWN"),
			labeledBy: (yelp_review.label_info.labeled_by_name ? yelp_review.label_info.labeled_by_name : "UNKNOWN"),
			labelNotes: (yelp_review.label_info.notes && yelp_review.label_info.notes.trim().length>0 ? yelp_review.label_info.notes : "NONE"),
			labeledDate: (moment(yelp_review.label_info.date).isAfter("1990-01-01T01:01:01Z") ? moment(yelp_review.label_info.date).format('MMM DD, YYYY - hh:mm a') : "NEVER"),
		
			isPartOfInvestigation:  (yelp_review.partOfInvestigation == null ? false : (yelp_review.partOfInvestigation!=0)),
			partOfInvestigation:    (yelp_review.partOfInvestigation == null ? 0 	:  yelp_review.partOfInvestigation),
			hasCompletedSurveys: 	(yelp_review.completedSurveys == null 	? false : (yelp_review.completedSurveys!=0)),
			completedSurveys : 		(yelp_review.completedSurveys == null 	? 0 	:  yelp_review.completedSurveys),
			hasLinkedRestaurants: 	(yelp_review.linkedRestaurants== null 	? false : (yelp_review.linkedRestaurants!=0)),
			linkedRestaurants: 		(yelp_review.linkedRestaurants==null 	? 0 	:  yelp_review.linkedRestaurants)

		};
	},

	getDocumentHtml: function (doc, isEditMode) {
		var self = this;
		var result = null;
		var card = self.makeYelpCard(doc.data);

		//card = self.makeClassifiable(card, doc, outbreak, "YES");
		card.isEditMode = isEditMode || !card.labeledDate;
		result = $($.Mustache.render('yelp-card', card));
		self.setDocumentLabels(result, card);
		return result;
	},

	makeClassifiable: function(card, doc, outbreak, defaultLinkLabel) {
		
		defaultLinkLabel = defaultLinkLabel || "UNKNOWN";
		card.documentId = doc.id;
		card.labeledBy = doc.labeledBy;
		card.labeledDate = doc.labeledDate ? moment(doc.labeledDate).format('MMM DD, YYYY') : null;
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
	// ------------- EVENTS ---------------
	// ------------------------------------

	readMore: function(e) {
		e.preventDefault();
		var yelpReviewId = $(e.currentTarget).data('id');
		$('#text_small_'+yelpReviewId).fadeOut();
		$('#text_large_'+yelpReviewId).fadeIn();
	},

	readLess: function(e) {
		e.preventDefault();
		var yelpReviewId = $(e.currentTarget).data('id');
		$('#text_large_'+yelpReviewId).fadeOut();
		$('#text_small_'+yelpReviewId).fadeIn();
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

	editDocumentLabel: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		var serial_id = documentCard.find('.mserial_id').html();

		//get latest snaphost of label
		var yp;
		$.ajax({
			async: false,
			url: '/api/detected_yelp/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					alert('Failed to get outbreak.');
				yp = apiResp;
			},
			error: function(data) {
				errorHandler("Failed to get outbreaks. The application appears to be down completely.");
			}
		});

		card  = self.yelpCardView(yp.data);
		card.serial_id = serial_id;
		card.isEditMode = true
		html = $.Mustache.render('yelp-review-card', card)
	   	//docCard = $(result);
	   	//docCard.find('dt[data-toggle="tooltip"]').tooltip();
		documentCard.replaceWith(html);
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

	updateDocument: function(e) {
		e.preventDefault();
		var self = this;

		var button = $(e.currentTarget);
		var documentId = button.data('id');
		var grade = button.parent();

		var document = {};
		document.docId 	= documentId;
		document.labelSeriousEnough = grade.find('.labelSeriousEnough').val();
		document.labelSomeoneGotSick = grade.find('.labelSomeoneGotSick').val();
		document.labelTimingConsistent = grade.find('.labelTimingConsistent').val();
		document.linkLabel = grade.find('.linkLabel').val();
		document.notes = grade.find('.notes').val();
		document.labeledDate = moment(); /* moment will use the current time from the current locale. Instead we keep track of the date server-side */
		var data = _.pick(document, 'docId', 'labelSeriousEnough', 'labelSomeoneGotSick', 'labelTimingConsistent', 'linkLabel', 'notes');
		console.log("data: " + JSON.stringify(data));

		$.ajax({
			type: 'PUT',
			data: JSON.stringify(data),
			contentType: 'application/json',
			url: '/api/detected_yelp/annotate/' + encodeURIComponent(documentId),
			success: function(apiResp) {
				console.log(apiResp.data);
				ccard  = self.yelpCardView(apiResp.data);
				console.log(ccard);
				ccard.isEditMode = false
				html = $.Mustache.render('yelp-review-card', ccard);
				grade.parents('.document-card').replaceWith(html);
			},
			error: function() {
				alert('An error occurred, please check your connection and try again');
			}
		});
	},
	// ------------------------------------
	// ---------- UTILITIES ---------------
	// ------------------------------------

	getMapUrl: function(lat, lon) {
		return 'https://www.google.com/maps/place/' + lat + ',' + lon;
	},

	getUnknownMapUrl: function() {
		alert('No location data is available for this business');
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

	clearForms: function(){
		$('.survey_row').html('');
		$('.survey_row').hide();

		$('.add-to-investigation-row').html('');
		$('.add-to-investigation-row').hide();
	},

	closeForms: function(e){
		e.preventDefault();
		var self = this;
		button = $(e.currentTarget);
		var documentId = button.data('id');
		var documentCard = button.parents('.document-card');
		self.clearForms(documentId, documentCard);
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
				//inv_table = self.makeInvestigationsTable(apiResp.data, inv_table, card, documentId);
				var investigations = documentCard.find('.add-to-investigation-row');
				investigations.show();
				investigations.html(card.html());
				card = self.makeInvTable(card, apiResp.data, documentId)
				
				
				$("#inv_table").on('click', '.add_inv', function(e){
					self.addInv(e);
				});
				
			},
			error: function(data) {
				console.log(JSON.stringify(data));
				errorHandler("Failed to get outbreaks. The application appears to be down completely.");
			}
		});
	},

	addInv: function(e){
		e.preventDefault();
		self = this;
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
		rid = documentCard.find('.bid').html();
		self.clearForms(documentId, documentCard);


		//start investigation
		console.log(documentId + " " + rid);
		$.ajax({
			url: '/api/investigations/start/' + documentId + '?business_id=' + urlEncode(rid),
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					return self.errorHandler('Failed to start investigation.');
				else if (!apiResp.success)
					return self.errorHandler('Failed to start investigation: ' + apiResp.error);
				self.successHandler('New investigation ' + apiResp.data + " just got created!");
			},
			error: function(data) {
				self.errorHandler("Failed to start investigation. The application appears to be down completely.");
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
			url: '/api/detected_yelp/' + documentId,
			dataType: 'json',
			success: function(apiResp) {
				if (!apiResp)
					self.errorHandler('Failed to get up-to-date information for tweet with Complaint Id: '+ documentId +'.');
				yp = apiResp;
				card  = self.yelpCardView(yp.data);
				card.serial_id = serial_id
				html = $.Mustache.render('yelp-review-card', card)
				button.parents('.document-card').replaceWith(html);
			},
			error: function(data) {
				self.errorHandler('Failed to get up-to-date information for tweet with Complaint Id: '+ documentId +'.');
			}
		});
	}
});