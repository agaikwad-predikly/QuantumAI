var $menu = $('#menu'),
	   $menulink = $('.menu-link'),
	   $menuTrigger = $('.has-submenu > a');

$menulink.click(function (e) {
	e.preventDefault();
	$menulink.toggleClass('active');
	$menu.toggleClass('active');
});

$menuTrigger.click(function (e) {
	e.preventDefault();
	var $this = $(this);
	$this.toggleClass('active').next('ul').toggleClass('active');
});


$.ajaxQ = (function () {
	var id = 0, Q = {};

	$(document).ajaxSend(function (e, jqx) {
		jqx._id = ++id;
		Q[jqx._id] = jqx;
	});
	$(document).ajaxComplete(function (e, jqx) {
		delete Q[jqx._id];
	});

	return {
		abortAll: function () {
			var r = [];
			$.each(Q, function (i, jqx) {
				r.push(jqx._id);
				jqx.abort();
			});
			return r;
		},
		get_remaining_cnt: function () {

			// Get the size of an object
			return  Object.size(Q);
		}
	};

})();



Object.size = function (obj) {
	var size = 0, key;
	for (key in obj) {
		if (obj.hasOwnProperty(key)) size++;
	}
	return size;
};