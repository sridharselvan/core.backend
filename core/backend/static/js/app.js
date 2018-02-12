
var app = angular.module("configuration", ['ui.router']);

app.factory('UserSessionService', function() {
  var sessionData = {
      session_cd : '',
      user_idn : ''
  };

  return {
      getSessionData: function () {
          return sessionData;
      },
      setSessionData: function (session_cd, user_idn) {
          sessionData.session_cd = session_cd;
          sessionData.user_idn = user_idn;
      }
  };

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
          user_idn = response.data.result.user_idn;
          UserSessionService.setSessionData(session_cd, user_idn);
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


//Start http

app.factory('http', ['$http', '$q', 'UserSessionService', '$state', 
  function($http, $q, UserSessionService, $state) {
    return {
      get: function(url) {
          var deferred =  $q.defer();
          $http.get(url, 
            {
              params: UserSessionService.getSessionData()
            }
          ).then(
            function(response) {
              if(response.data.is_session_valid){
                deferred.resolve(response);
              } else {
                $state.transitionTo('login');
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
        formData["sessionData"] = UserSessionService.getSessionData();
        $http.post(url, 
          {formObj: formData,
            params: UserSessionService.getSessionData()
          })
          .then(
          function(response) {
            if(response.data.is_session_valid){
              deferred.resolve(response);
            } else {
              $state.transitionTo('login');
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
