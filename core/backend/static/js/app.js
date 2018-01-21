
var app = angular.module("configuration", ['ui.router']);


//Start: controller: LoginPageController
app.controller('loginController', function($scope, $http, $state, $stateParams){

  $scope.logindata = {rememberMe : 'false'};

  $scope.loginVaidation = function(){
    $http
      .post('/loginvalidation', {'formObj' : $scope.logindata})
      .then(function(response) {
        if(response.data.result){
          $state.transitionTo('home.dashboard');
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
              alert(response.data.msg);
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
  
  $stateProvider.state(loginState);
  $stateProvider.state(signUpState);

  $stateProvider
    .state('home', {
      abstract: true,
      templateUrl: 'home_page.html',
  })

  .state('home.dashboard', {
    url: '/dashboard',
    views: {
      'mainPage': {
        templateUrl: "dashboard_page.html"
      }
    },
    name: 'Home'
  })

  .state('home.configuration', {
    url: '/configuration',
    views: {
      'subPage': {
        templateUrl: "config_page.html"
      }
    },
    name: 'Configuration'
  })

  .state('home.log', {
    url: '/log',
    views: {
      'subPage': {
        templateUrl: "log_page.html"
      }
    },
    name: 'Log'
  })
  

  // Route to Home Page if any wrong url is given
  $urlRouterProvider.otherwise('/');

  //

  app.run(['$rootScope', function($rootScope) {
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
        $rootScope.title = current.$$route.name;
    });
  }]);
});
