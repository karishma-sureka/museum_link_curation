
angular.module('MyApp',['ngMaterial', 'ngMessages', 'material.svgAssetsCache'])

.controller('AppCtrl', function($scope) {
  $scope.title1 = 'Button';
  $scope.title4 = 'Warn';
  $scope.isDisabled = False;

  $scope.googleUrl = 'http://google.com';

});


/**
Copyright 2016 Google Inc. All Rights Reserved. 
Use of this source code is governed by an MIT-style license that can be in foundin the LICENSE file at http://material.angularjs.org/license.
**/