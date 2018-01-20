
var app = angular.module("configuration", ['ui.router']);

//Start: controller: LoginPageController
app.controller('loginController', function($scope, $http, $state, $stateParams){

  $scope.logindata = {rememberMe : 'false'};

  $scope.loginVaidation = function(){
    $http
      .post('/loginvalidation', {'formObj' : $scope.logindata})
      .then(function(response) {
        if(response.data.result){
          $state.transitionTo('configuration');
        }else{
          $scope.errorMsg = 'Invalid username/password';
        }
    });
  }

  $scope.signUpValidation = function(){
    $state.transitionTo('signUp');
  }
  
}); //End: controller: LoginPageController


//Start: controller: SignUpPageController
app.controller('signUpController', function($scope, $http, $state, $stateParams){

  $scope.userDetails = {};

  /*var s =angular.element(document).find("#xxx");
  s[0].innerText = "qqqq";
  console.log(s)*/;

  $scope.CreateUserValidation = function(){
    $http
      .post('/createUser', {'formObj' : $scope.userDetails})
      .then(function(response) {
        console.log(response);
        $state.transitionTo('login');
    });
  }

  $scope.signUpValidation = function(){
    $state.transitionTo('signUp');
  }
  
}); //End: controller: SignUpPageController


//Start: controller:clientConfigController
app.controller("clientConfigController", function($scope, $http) {

    //Update the form data to client ini fiile
    $scope.saveConfig = function () {
        $http
            .post(
                '/modifyclientconfig',
                {formObj: $scope.serverData}
            ).then(function(response) {
                alert(response.data);
            });
    }

    /** Runs during page load.*/
    $http
        .get("/viewclientconfig")
        .then(function (response) {
            $scope.serverData = response.data;
        });

}); // end: controller:clientConfigController


app.config(function($stateProvider, $urlRouterProvider) {
  var loginState = {
    name: 'login',
    url: '/',
    templateUrl: '/login_page.html'
  }

  var signUpState = {
    name: 'signUp',
    url: '/signup',
    templateUrl: '/signup_page.html'
  }

  var configState = {
    name: 'configuration',
    url: '/viewclientconfig',
    templateUrl: '/config_page.html',
    controller: 'clientConfigController'
  }

  $stateProvider.state(loginState);
  $stateProvider.state(configState);
  $stateProvider.state(signUpState);

  // Set Home Page as default
  $urlRouterProvider.when('', '/')

  // Route to Home Page if any wrong url is given
  $urlRouterProvider.otherwise('/')
});
