
var app = angular.module("configuration", ['ui.router']);

app.factory('UserSessionService', function() {
  var sessionData = {
      session_cd : '',
      user_name : ''
  };

  return {
      getSessionData: function () {
          return sessionData;
      },
      setSessionData: function (session_cd, user_name) {
          sessionData.session_cd = session_cd;
          sessionData.user_name = user_name;
      }
  };

  return sessionData;
});

//Start: controller: LoginPageController
app.controller('loginController', function($scope, $http, $state, $stateParams, UserSessionService){

  $scope.logindata = {rememberMe : 'false'};

  $scope.loginVaidation = function(){
    $http
      .post('/loginvalidation', {'formObj' : $scope.logindata})
      .then(function(response) {
        if(response.data.status){
          //Setting session values
          var session_cd = response.data.result.user_session_cd,
          user_name = response.data.result.user_name;
          UserSessionService.setSessionData(session_cd, user_name);
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


//Start: controller:clientConfigController
app.controller("clientConfigController", function($scope, $http, $state, UserSessionService) {

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
        .get("/viewclientconfig", {
          params: UserSessionService.getSessionData()
        })
        .then(function (response) {
            if(response.data.is_session_valid){
              $scope.serverData = response.data;
            } else {
              $state.transitionTo('login');
            }
        });

}); // end: controller:clientConfigController


app.config(function($stateProvider, $urlRouterProvider, $httpProvider) {

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

/*  app.run(['$rootScope', function($rootScope) {
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
        $rootScope.title = current.$$route.name;
    });
  }]);*/
});
