(function(){
	var app = angular.module('timeline', []);

	app.controller('TagsController', [ '$http', function($http){
		var store = this;
		store.tag_list = [];
		$http.get('/tags/').success(function(data){
			store.tag_list = data.tags;
		});
	} ]);

})();
