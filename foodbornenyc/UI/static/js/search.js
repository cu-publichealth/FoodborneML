
// Takes the id of the button pressed -- use this to figure out if twitter or yelp view should be called
function newsearch(id) {
	searchtype = document.getElementsByClassName('page-header')[0].id.substring(
				'results-'.length).toLowerCase()
	page = 1	
	search(searchtype, page)
}

// Search using form parameters
function search(type, page) {
	// Get search form values
	threshold = document.getElementById('thr').value
	st_date = document.getElementById('dt_start').value
	end_date = document.getElementById('dt_end').value
	order_by = document.getElementById('order_by').value

	// Set number of results
	num_results = document.getElementById('results_num').value
	query_str = 'thr=' + threshold

	//Construct query
	if (st_date != "") {
		query_str += '&start_date=' + st_date
	}
	if(end_date != ""){
		query_str += '&end_date=' + end_date
	}
	query_str += '&order_by=' + order_by + '&num_results=' + num_results + '&page=' + page

	// Reset url to call flask view
	window.location.href = '/' + searchtype + '?' + query_str;
}

function next(id) {
	searchtype = document.getElementsByClassName('page-header')[0].id.substring(
				'results-'.length).toLowerCase()
	page = document.getElementsByClassName('next-page')[0].id.substring(
										'next-page-'.length + searchtype.length + 1);
	console.log(page)
	search(searchtype, Number(page) + 1);
}

function prev(id) {
	searchtype = document.getElementsByClassName('page-header')[0].id.substring(
				'results-'.length).toLowerCase()
	page = document.getElementsByClassName('next-page')[0].id.substring(
										'next-page-'.length + searchtype.length + 1);
	console.log(page)
	search(searchtype, Number(page) - 1);
}




