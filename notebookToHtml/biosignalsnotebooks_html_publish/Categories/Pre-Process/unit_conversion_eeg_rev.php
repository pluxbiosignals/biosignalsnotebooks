<html>
<head>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-38036509-7"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'UA-38036509-7');
</script>
<meta charset="UTF-8">
<title>Notebook - unit conversion eeg</title>
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.5.0/css/all.css" integrity="sha384-B4dIYHKNBt8Bc12p+WXckhzcICo0wtJAoU8YZTY5qE0Id1GSseTk6S+L3BlXeVIU" crossorigin="anonymous">
<script   src="https://code.jquery.com/jquery-3.3.1.min.js"   integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="   crossorigin="anonymous"></script>
<link href="../../notebooks.css" rel="stylesheet" type="text/css">
</head>

<body onLoad="loadNotebook()">
	<div id="wrap-me">
		<div id="header-bio" class="clearHeader ">
			<?php include "../../notebooks-hd.php";?></div>
		<div id="main-bio">
			<div id="notebook-include"></div>	
		</div>
		<div id="footer-bio">
			<?php include "../../notebooks-ft.php"; ?></div>
	</div>

	<script>
	/*header hide and show*/
	$(function() {
		var header = $("#header-bio");
		$(window).scroll(function() {
			var scroll = $(window).scrollTop();

			if (scroll >= 200) {
				header.removeClass('clearHeader').addClass("hideHeader");
			} else {
				header.removeClass("hideHeader").addClass('clearHeader');
			}
		});
	});
	/*notebook links related stuff*/
	function loadNotebook(){
		var loadLink = "unit_conversion_eeg_rev.html";
		$("#notebook-include").load(loadLink); 
	};
	</script> 
</body>
</html>