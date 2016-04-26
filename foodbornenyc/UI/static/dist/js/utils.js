/*
 *	formatDate:
 *		input: Date object
 *		output: YYYY-MM-DD representation of Date
 */
function formatDate(td)
{
	var dd = td.getDate();
	var mm = td.getMonth()+1;
	var yyyy = td.getFullYear();

	if(dd < 10)
		dd ='0' + dd;

	if(mm < 10)
    mm = '0'+mm;

	return yyyy + '-' + mm + '-' + dd;
}



function d2t(dateString)
{
	var dateParts = dateString.split(" ");
	var timeParts = dateParts[1].split(":");
	dateParts = dateParts[0].split('/');
	if(dateString.indexOf("PM") > -1){
		t = parseInt(timeParts[0], 10) + 12;
		date = new Date(dateParts[2], parseInt(dateParts[0], 10) - 1, dateParts[1], t, timeParts[1]);
	}else{
		t = parseInt(timeParts[0], 10);
		date = new Date(dateParts[2], parseInt(dateParts[0], 10) - 1, dateParts[1], t, timeParts[1]);
	}
	return date.getTime();
}


//////////////////////////////////////
///									//
///       URI ENCODING-DECODING		//
///									//
//////////////////////////////////////
function urlEncodeCharacter(c)
{
	return '%' + c.charCodeAt(0).toString(16);
};

function urlDecodeCharacter(str, c)
{
	return String.fromCharCode(parseInt(c, 16));
};

function urlEncode( s )
{
	return encodeURIComponent( s ).replace( /\%20/g, '+' ).replace( /[!'()*~]/g, urlEncodeCharacter );
};

function urlDecode( s )
{
	return decodeURIComponent(s.replace( /\+/g, '%20' )).replace( /\%([0-9a-f]{2})/g, urlDecodeCharacter);
};