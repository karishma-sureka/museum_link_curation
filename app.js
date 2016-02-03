/**
 * Created by ksureka on 2/1/16.
 */
var app = angular.module('linkCuration', []);

app.controller('MainCtrl', [
    '$scope',
    function($scope){
        $scope.test = 'Museum Data comes here';

        $scope.questions = [
            {title: 'question 1', answers: 5},
            {title: 'question 2', answers: 2},
            {title: 'question 3', answers: 15},
            {title: 'question 4', answers: 9},
            {title: 'question 5', answers: 4}
        ];

        $scope.addComment = function(){
            if(!$scope.title || $scope.title === '') { return; }
            $scope.posts.push({title: $scope.title, answers: 0});
            $scope.title = '';
        };

        $scope.incrementAnswers = function(question) {
            question.answers += 1;
        };
    }]);
