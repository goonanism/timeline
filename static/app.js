(function(){
	var app = angular.module('timeline', []);
	app.controller('TagsController', function($scope, $http){
		$scope.tag_list = null;
		$http({
			method: 'GET',
			url: '/tags/'
		}).success(function(result){
			$scope.tag_list = result.tags;
		});
	});
})();
