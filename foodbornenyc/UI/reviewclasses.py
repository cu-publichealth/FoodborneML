
# Parent class for reviews
class Review(object):
    def __init__(self, business, review, score, created, reviewtype):
        self.business = business     
        self.review = review
        self.score = score
        self.reviewtype = reviewtype
        self.created = created
        #self.feedback = 'Give feedback'

# Subtype of Review for yelp reviews
class UIYelpReview(Review):
    def __init__(self, business, review, score, created, review_type, username, yelp_id):
        Review.__init__(self, business, review, score, created, review_type)
        self.username = username
        self.id = yelp_id

# Subtype of Review for tweets
class UITwitterReview(Review):
    def __init__(self, business, review, score, created, review_type, username, yelp_id):
        Review.__init__(self, business, review, score, created, review_type)
        self.username = username
        self.id = yelp_id

# Reviews have business object as an instance variable
class UIBusiness(object):
    def __init__(self, id, name, phone, rating, url, business_url):
        self.id = id
        self.name = name
        self.phone = phone
        self.rating = rating
        self.url = url
        self.business_url = business_url