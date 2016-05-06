/*
 *	Filename: wajax.js
 *	Project: Wooffer
 *	Time: Tuesday 6-1-2012
 *	Implemented by: Psallidas Fotis
 */

/*
*	function changeLang
*		* param1 : lang -> (en,gr)
*		* functionality: change language using ajax
*/ 
function changeLang(lang) {
    "use strict";
	if (lang) {
		var datastr = "lang=" + lang;
		$.ajax({	
			type: "POST",
			url: "php/change_lang.php",
			data: datastr,
			cache: false,
			success: function(html){
				location.reload(true);
			}
		});
	}
}

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


function do_login(){
	var username = $("#login_username").val();
	var password = $("#login_password").val();
	var datastr = "username=" + urlEncode(username) + "&password=" + urlEncode(password) + "&requestType=1";
	$("#login_message").fadeIn("slow");
	$("#login_message").html("<p style=\"text-align: center;\">&nbsp&nbsp<b>Sending Request<br/>Please Wait...</b><br/><img src=\"img/ajax-loaders/ajax-loader-7.gif\" alt=\"\" title=\"\"/> <br/></p>");
	setTimeout("loginUser('"+datastr+"')",1000);
}

function loginUser(datastr){
	$.ajax({
		type: "POST",
		url:  "php/processRequest.php",
		data: datastr,
		cache: false,
		success: function (html) {
			var ret = eval("("+html+")");
            if(ret.success==false){
                $("#login_message").html(" <p style=\"text-align: center;\"><div style=\"float:left;\"><img style=\"border: none; margin: 0px; padding: 0px;\" src=\"./img/template/error.png\" "
                                +" width=\"24px\" height=\"24px\" alt=\"Name Error\"/ ></div><div style=\" margin-top:0px; margin-left:30px; "
                                +" margin-right:5px; font-size:9pt\"><b>"+ret.en_description+"</b> </div></p>") ;
            }else{
                $("#login_message").html(" <p style=\"text-align: center;\"><div style=\"float:left;\"><img style=\"border: none; margin: 0px; padding: 0px;\" src=\"./img/template/ok.png\" "
                                +" width=\"24px\" height=\"24px\" alt=\"Name Error\"/ ></div><div style=\" margin-top:0px; margin-left:30px; "
                            +" margin-right:5px; font-size:9pt\"><b>"+ret.en_description+"<br/><br/>In case of no redirection, follow the <a href=\"index.php\">link</a> to enter.</b> </div></p>");
                window.location = "index.php";
            }
		}
	});
}

