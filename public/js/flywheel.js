$(document).ready(function() {
	
	var GATrafficSource = (function(){
			var pairs = (/(?:^|; )__utmz=([^;]*)/.exec(document.cookie)||[]);
			if(pairs.length > 0){
				pairs = pairs.slice(1);
				pairs = pairs.pop();
				pairs = pairs.split('.');
				pairs = pairs.slice(4);
				pairs = pairs.join('.');
				pairs = pairs.split('|');
			}
			var vals = {};
			
			for (var i = 0; i < pairs.length; i++) {
				var temp = pairs[i].split('=');
				vals[temp[0]] = temp[1];
			}
			var retval = {
				'utm_source': (vals.utmgclid) ? "google" : vals.utmcsr,
				'utm_medium': (vals.utmgclid) ? "cpc" : vals.utmcmd,
				'utm_campaign': vals.utmccn,
				'utm_content': vals.utmcct,
				'utm_term': vals.utmctr
			};
			return retval;
	}());
	
	// auto fill hidden fields for GA parsing
	$("#Source, #Source2").val(GATrafficSource.utm_source);
	$("#Campaign, #Campaign2").val(GATrafficSource.utm_campaign);
	$("#Medium, #Medium2").val(GATrafficSource.utm_medium);
	$("#Keywords, #Keywords2").val(GATrafficSource.utm_term);
	
	$('a[href*=#]').click(function() {
	    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')
	    && location.hostname == this.hostname) {
	      var $target = $(this.hash);
	      $target = $target.length && $target
	      || $('[name=' + this.hash.slice(1) +']');
	      if ($target.length) {
	        var targetOffset = $target.offset().top;
	        $('html,body')
	        .animate({scrollTop: targetOffset}, {duration: 1000, easing: 'easeInOutExpo'});
	       return false;
	      }
	    }
	  });
	
	// default values in forms
	$('#subForm .email').watermark();
	$('#name-field').watermark();
	$('#email-field').watermark();
	$('#phone-field').watermark();
	$('#company-field').watermark();
	$('#comments-field').watermark();
	$('#author').watermark();
	$('#email').watermark();
	$('#url').watermark();
	$('#comment').watermark();
	/*$('.flywheel-form input[type="text"], .flywheel-form input[type="email"]').focus(function(){
		if($(this).val() == $(this).attr("data-value"))
			$(this).val("");
	})*/

	
	//validate forms
	$(".flywheel-form").each(function() {
		$(this).validate();
	});
	
	// show contact form
	$(".contact-link").click(function(){
		$(".contact-form").show();
		return false;
	})
	
	$(".scroll-top").click(function(){
		$('.sign-up-form .watermark').stop().css("color", "#F57E27");
	})
	
	//thank you modal
	if($(".thank-you-modal").length != 0){
		$(".thank-you-modal").modal({
			opacity:80,
			overlayCss: {backgroundColor:"#000"},
			overlayClose: true,
			closeClass: "close-modal"
		});
	}
	if($(".subscribe-modal").length != 0){
		$(".subscribe-modal").modal({
			opacity:80,
			overlayCss: {backgroundColor:"#000"},
			overlayClose: true,
			closeClass: "close-modal"
		});
	}
	$(".contact-link, .switch-link").click(function(){
		$("html, body").animate({scrollTop: $(document).height()}, {duration: 1000, easing: 'easeInOutExpo'});
		  return false;
	})

	if($(".image-modal").length != 0){
		$(".faq-wrap img").click(function(e){
			e.preventDefault();
			var image = $(this).attr("src");
			var image_html = '<img src="' + image + '" width="100%">';
			$(".image-modal .image-wrap").html(image_html);
			$(".image-modal").modal({
				opacity:80,
				overlayCss: {backgroundColor:"#000"},
				overlayClose: true,
				closeClass: "close-modal"
			});
		})
	}
	
	/* blog post masonry */
	$('.more-posts-masonry').masonry({
	  itemSelector: '.more-posts-wrap'
	});
	$(window).resize(function() {
	  	$('.more-posts-masonry').masonry({
		  itemSelector: '.more-posts-wrap'
		});
	});
	$(".more-posts-wrap").mouseover(function(){
		$(this).addClass("hovering");
	})
	$(".more-posts-wrap").mouseleave(function(){
		$(this).removeClass("hovering");
	})
	$(".more-posts-wrap").click(function(){
		window.location = $(this).find("a").attr("href");
	})
	$(".has-sub-nav").mouseover(function(){
		$(this).addClass("hovering");
	})
	$(".has-sub-nav").mouseleave(function(){
		$(this).removeClass("hovering");
	})
	
	/* lock form on scroll */
	$('.down-tab, .reasons-wrap .flywheel-blurb h3 span').waypoint(function(event, direction) {
	   if (direction === 'down') {
	      $('.lock-header').animate({
		    top: '0'
		  }, 200, function() {
		    // Animation complete.
		  });
	   }
	   else {
	      $('.lock-header').animate({
		    top: '-70px'
		  }, 200, function() {
		    // Animation complete.
		  });
	   }
	});
	$('.icon-heart, .reason-5-parallax').waypoint(function(event, direction) {
	   if (direction === 'down') {
			$('.lock-header').animate({
				top: '-70px'
			}, 200, function() {
			// Animation complete.
			});
	   }
	   else {
	      $('.lock-header').animate({
		    top: '0px'
		  }, 200, function() {
		    // Animation complete.
		  });
	   }
	});
	
	
	// switch page toggle
	$(".lock-header .more").click(function(){
		$(".lock-header .toggle li").removeClass("active");
		$(this).parent().addClass("active");
		$(".reasons-wrap .non-techy").hide();
		$(".reasons-wrap .techy").show();
		return false;
	})
	$(".lock-header .less").click(function(){
		$(".lock-header .toggle li").removeClass("active");
		$(this).parent().addClass("active");
		$(".reasons-wrap .non-techy").show();
		$(".reasons-wrap .techy").hide();
		return false;
	})
	$('.reason-2-parallax, .reason-3-parallax, .reason-4-parallax, .reason-5-parallax').parallax('50%', .5);
	$('.reason-1-parallax').parallax('50%', .5);
	

	$('.sign-up-form, .sign-up-form-fixed').submit(function() {
		_kmq.push(['identify', $(this).find(".email").val()]);
		_kmq.push(['record', 'Subscribed']);
	});
});