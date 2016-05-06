var OutbreakView = Backbone.View.extend({

	events : {
		"click .outbreak-card" : 			"showOutbreak",
		"click .outbreak-card-positive" : 	"showOutbreak",
		"click .outbreak-card-negative" : 	"showOutbreak",
		"click .outbreak-back" : 			"showAllOutbreaks"
	},

	initialize : function() {
		var self = this;

		self.outbreaks = outbreaks;

		self.render();
	},

	// ------------------------------------
	// ------------- RENDER ---------------
	// ------------------------------------

	render : function() {
		var self = this;

		self.$el.html('');

		var outbreaks = self.$el.mustache('outbreaks', null);

		var cardsHtml = "";
		_.each(self.outbreaks, function(outbreak) {
			if (outbreak.label == "YES") {
				cardsHtml += $.Mustache.render('outbreak-card-positive', self.outbreakCardView(outbreak));
			}
			else if (outbreak.label == "NO") {
				cardsHtml += $.Mustache.render('outbreak-card-negative', self.outbreakCardView(outbreak));	
			}
			else {
				cardsHtml += $.Mustache.render('outbreak-card', self.outbreakCardView(outbreak));
			}
		});

		outbreaks.find('.outbreak-cards').html(cardsHtml);
	},

	outbreakCardView : function(outbreak) {
		return outbreak;
	},

	techToView : function() {
		var self = this;

		var user = '';
		var hasMap = false;
		var mapUrl = 'http://maps.google.com/maps/api/staticmap?size=640x640&sensor=false';

		var getMarker = function(color, lat, lon) {
			return '&markers=color:' + color + '|' + lat + ',' + lon;
		};

		_.each(self.current.tweets, function(tweet) {
			if (tweet.loc && tweet.loc.length > 0) {
				hasMap = true;
				mapUrl += getMarker('red', tweet.loc[1], tweet.loc[0]);
			}
			if (tweet.initial) {
				user = tweet.user;
			}
		});

		var t = {
			date : moment(tweet.date).format('MMM DD, HH:mm'),
			text : tweet.text,
			user : tweet.user,
			css  : ''
		};
		
		if (tweet.loc && tweet.loc.length > 0) {
			t.loc = tweet.loc[1].toFixed(2) + ', ' + tweet.loc[0].toFixed(2);
			t.locUrl = 'https://www.google.com/maps/place/' + tweet.loc[1] + ',' + tweet.loc[0];
		}

		return {
			user      : user,
			mapUrl    : hasMap ? mapUrl : null
		};
	},

	// ------------------------------------
	// ------------- EVENTS ---------------
	// ------------------------------------

	showOutbreak : function(e) {
		e.preventDefault();
		var self = this;


	},

	showAllOutbreaks : function(e) {
		e.preventDefault();
		var self = this;

		self.render();
	},

	// ------------------------------------
	// ---------- UTILITIES ---------------
	// ------------------------------------

	getMapUrl : function(coord) {
		return 'https://www.google.com/maps/place/' + coord[1] + ',' + coord[0];
	},

	getMultiMapUrl : function(coordsWithColor) {
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
