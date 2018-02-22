
var app = angular.module("configuration", ['ui.router']);


//Start: controller: LoginPageController
app.controller('loginController', function($scope, $http, $state, $stateParams){

  $scope.logindata = {rememberMe : 'false'};

  $scope.loginVaidation = function(){
    $http
      .post('/loginvalidation', {'formObj' : $scope.logindata})
      .then(function(response) {
        if(response.data.status){
          //Redirect to home page
          $state.transitionTo('home.dashboard');
        }else{
          $scope.errorMsg = response.data.msg;
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

  $scope.CreateUserValidation = function(){
    $http
      .post('/createUser', {'formObj' : $scope.userDetails})
      .then(function(response) {
        $state.transitionTo('login');
    });
  }

  $scope.signUpValidation = function(){
    $state.transitionTo('signUp');
  }
  
}); //End: controller: SignUpPageController


//Start: controller: LogoutController
app.controller('menuController', function($scope, http, $state, $stateParams){

    $scope.logout = function(){

      if(confirm('Are you sure you want to logout this?')){
        http
          .get('/logoutuser')
          .then(function(response) {
            $state.transitionTo('logout');
        });
      }
    }
  
}); //End: controller: LogoutController


//Start: controller:clientConfigController
app.controller("clientConfigController", function($scope, http, $state) {

    /** Runs during page load.*/
    _loadClientConfig = function(){
      http.get("/viewclientconfig")
        .then(function(response){
          $scope.serverData = response.data;
      });
    }

    _loadClientConfig();

    //Update the form data to client ini fiile
    $scope.saveConfig = function () {

      http.post("/modifyclientconfig", $scope.serverData)
        .then(function(response){
          $scope.serverData = response.data;
          _loadClientConfig();
      });
    }

}); // end: controller:clientConfigController

//Start: controller:schedulerController
app.controller("schedulerController", function($scope, http, $state, $filter) {

  $scope.schedulerData = {
    type:null,
    date: {
      day : $filter('date')(new Date(), 'd'),
      month : $filter('date')(new Date(), 'M'),
      year : $filter('date')(new Date(), 'yyyy'),
      hour : $filter('date')(new Date(), 'H'),
      mins : $filter('date')(new Date(), 'm'),
    }
  };
  $scope.range = function(min=1, max, step) {
    step = step || 1;
    var input = [];
    for (var i = min; i <= max; i += step) {
        input.push(i);
    }
    return input;
  };

}); // end: controller:schedulerController


//Start http

app.factory('http', ['$http', '$q', '$state', 
  function($http, $q, $state) {
    return {
      get: function(url) {
          var deferred =  $q.defer();
          $http.get(url).then(
            function(response) {
              if(response.data.is_session_valid){
                deferred.resolve(response);
              } else {
                $state.transitionTo('logout');
              }
            },
            function(response) {
                deferred.reject(response)
            }
          );
          return deferred.promise;
      },

      post: function(url, formData) {
        var deferred =  $q.defer();
        $http.post(url, {formObj: formData}).then(
          function(response) {
            if(response.data.is_session_valid){
              deferred.resolve(response);
            } else {
              $state.transitionTo('logout');
            }
          },
          function(response) {
              deferred.reject(response)
          }
        );
        return deferred.promise;
      }
    };
}]);

//End http

app.config(function($stateProvider, $urlRouterProvider, $httpProvider) {

  var loginState = {
    name: 'login',
    url: '/',
    templateUrl: '/login_page.html'
  };

  var signUpState = {
    name: 'signUp',
    url: '/signup',
    templateUrl: '/signup_page.html'
  };

  var logoutState = {
    name: 'logout',
    url: '/logout',
    templateUrl: '/logout_page.html'
  }
  
  $stateProvider.state(loginState);
  $stateProvider.state(signUpState);
  $stateProvider.state(logoutState);

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

  .state('home.scheduler', {
    url: '/scheduler',
    views: {
      'subPage': {
        templateUrl: "scheduler_page.html"
      }
    },
    name: 'Scheduler'
  })
  

  // Route to Home Page if any wrong url is given
  $urlRouterProvider.otherwise('/');

});
