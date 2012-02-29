$(document).ready(function() {
	// init. clearing of input values on initial click only
	/*
	function clearOnInitialFocus( fieldName ){
		var clearedOnce = false;

		document.getElementById( fieldName ).onfocus = (function(){
			if (clearedOnce == false){
				this.value = '';
				clearedOnce = true;
			}
		})
	}
	window.onload = function(){
		clearOnInitialFocus('username');
		clearOnInitialFocus('password');
	};
	*/

	// hide product names in gallery thumbnails
	$('.cat-product-gal-name').css({
		bottom: '-40px',
	});

	// initiate rollover
	$('.cat-product-gal-thumb').hover(
	function(){
		$(this).children('.cat-product-gal-name').stop().animate({
			bottom: '0px'
		}, 75)
	},
	function(){
		$(this).children('.cat-product-gal-name').stop().animate({
			bottom: '-40px'
		}, 75)
	});
});