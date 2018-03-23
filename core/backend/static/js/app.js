
var app = angular.module("configuration", ['ui.router', 'ui.bootstrap']);


//Start: controller: LoginPageController
app.controller('loginController', function($scope, $http, $state, $stateParams){

  $scope.logindata = {};

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
app.controller("schedulerController",['$scope', 'http', '$state', '$filter', '$window', '$modal', '$rootScope',
  function($scope, http, $state, $filter, $window, $modal, $rootScope) {

    $scope.tab = 1;
    $scope.showSuccessMsg = false;

    $scope.setTab = function(newTab){
      $scope.tab = newTab;
      if(newTab == 1){
        angular.element('#newScheduler').addClass("active");
        angular.element('#searchScheduler').removeClass("active");
      } else {
        angular.element('#newScheduler').removeClass("active");
        angular.element('#searchScheduler').addClass("active");
      }
    };

    $scope.isSet = function(tabNum){
      return $scope.tab === tabNum;
    };

  $scope.types = ['Select One', 'OneTime', 'Daily', 'Weekly'];  
  $scope.schedulerData = {
    type:$scope.types[0],
    start_date: {
      day : $filter('date')(new Date(), 'dd'),
      month : $filter('date')(new Date(), 'MM'),
      year : $filter('date')(new Date(), 'yyyy'),
      hour : $filter('date')(new Date(), 'HH'),
      mins : $filter('date')(new Date(), 'mm'),
    },
    recurs:[],
    weekDays:[
      {id:'sun', value:'S', selected:false},
      {id:'mon', value:'M', selected:false},
      {id:'tue', value:'T', selected:false},
      {id:'wed', value:'W', selected:false},
      {id:'thu', value:'T', selected:false},
      {id:'fri', value:'F', selected:false},
      {id:'sat', value:'S', selected:false}
    ],
    ValveDetails:[]
  };
  

  /** Update recurs in scheduler data obj **/
  $scope.updateRecurs = function(){
    
    var max = ($scope.schedulerData.type.toLowerCase() == 'weekly') ? 5 : 31;
    $scope.schedulerData.recurs = [];
    for(var i=1;i<=max;i++){
      var j = (i<10) ? '0'+i : i;
      $scope.schedulerData.recurs.push({id:i, value:j, selected:false})
    };
  };

  $scope.selectAllDays = function(){
    var frequency = $scope.schedulerData.recurs;
    for(var i=0;i<frequency.length;i++){
      $scope.schedulerData.recurs[i]['selected'] = !frequency[i]['selected'];
    }
  };

  $scope.selectAllWeekDays = function(){
    var weekDays = $scope.schedulerData.weekDays;
    for(var i=0;i<weekDays.length;i++){
      $scope.schedulerData.weekDays[i]['selected'] = !weekDays[i]['selected'];
    }
  };

  /** Runs during page load.*/
    _loadClientConfig = function(){
      http.get("/viewclientconfig")
        .then(function(response){
          var nodeList = response.data.nodes.ids.split(' ');
          angular.forEach(nodeList, function(value) {
            $scope.schedulerData.ValveDetails.push(
              {
                id: response.data[value].id,
                name: response.data[value].name,
                selected:true
              }
            );
          });
      });
    }

    _loadClientConfig();

  $rootScope.$on('eventName', function (event, args) {
   $scope.SearchScheduledJob();
  });  

  $scope.triggerScheduler = function(){

    http
      .post('/saveschedulerconfig', $scope.schedulerData)
      .then(function(response) {
        $scope.showSuccessMsg = true;
        $scope.schedulerData.type = $scope.types[0];
    });
  }

  $scope.showSearchResult = false;
  $scope.searchScheduledData = {
    searchScheduleType : $scope.types[0]
  };

  $scope.SearchScheduledJob = function(){
    http
      .post('/searchscheduledjob', $scope.searchScheduledData)
      .then(function(response) {
        $scope.showSearchResult = true;
        $scope.scheduledJobDetails = response.data.data;
    }); 
  };

  $scope.deactivateScheduledJob = function(jobDetailsIdn) {
    http
      .post('/deactivatescheduledjob', {'job_details_idn' : jobDetailsIdn})
      .then(function(response) {
        $window.alert("Deactivated successfully");
    }); 
  };

  $scope.editScheduledJob = function(scheduledJob) {
    var modalInstance = $modal.open({
      templateUrl: 'edit-scheduled-event.html',
      controller: 'editScheduledController as editCtrl',
      resolve: {
         editData: function () {
           return scheduledJob;
         }
       },
       size: 'lg'
    });
  }

  $scope.range = function(min=1, max, step) {
    step = step || 1;
    var input = [];
    for (var i = min; i <= max; i += step) {
      if(i<10){
        input.push("0"+i);
      }else{
        input.push(i);
      }
    }
    return input;
  };

}]); // end: controller:schedulerController

//Start: controller:editScheduledController
app.controller("editScheduledController",['$scope', '$modalInstance', 'editData', 'http', '$state', '$rootScope',
  function($scope, $modalInstance, editData, http, $state, $rootScope) {

    var formData = editData, 
        start_date_time = formData.start_date.split(" "),
        start_date = start_date_time[0].split("-"),
        start_time = start_date_time[1].split(":"),
        dayOfWeek = formData.day_of_week.split(","),
        dayOfWeek = dayOfWeek.map(s => s.trim()),
        recurrence = formData.recurrence;

    $scope.editFormData = {
      job_id: formData.job_id,
      job_details_idn: formData.job_details_idn,
      type:formData.schedule_type,
      start_date: {
        day : start_date[2],
        month : start_date[1],
        year : start_date[0],
        hour : start_time[0],
        mins : start_time[1],
      },
      recurs:[],
      weekDays:[
        {id:'sun', value:'S', selected:false},
        {id:'mon', value:'M', selected:false},
        {id:'tue', value:'T', selected:false},
        {id:'wed', value:'W', selected:false},
        {id:'thu', value:'T', selected:false},
        {id:'fri', value:'F', selected:false},
        {id:'sat', value:'S', selected:false}
      ],
      ValveDetails:[]
    };

/*    for(var i=1;i<=max;i++){
      var j = (i<10) ? '0'+i : i;
      $scope.schedulerData.recurs.push({id:i, value:j, selected:false})
    };
*/
    for(var i=1; i<=recurrence.length; i++){
      var j = (i<10) ? '0'+i : i;
      if(parseInt(recurrence[i-1]) !== -1)
        $scope.editFormData.recurs.push({id:i, value:j, selected:true});
      else
        $scope.editFormData.recurs.push({id:i, value:j, selected:false});
    }

    angular.forEach($scope.editFormData.weekDays, function(day){
      if(dayOfWeek.indexOf(day.id) > -1) {
        day.selected = true
      }
    });

    $scope.updateScheduler = function(){
      http
        .post('/updateschedulerconfig', $scope.editFormData)
        .then(function(response) {
          $rootScope.$emit('eventName', {});
          $modalInstance.close('yes');
      });
    }

    $scope.range = function(min=1, max, step) {
      step = step || 1;
      var input = [];
      for (var i = min; i <= max; i += step) {
        if(i<10){
          input.push("0"+i);
        }else{
          input.push(i);
        }
      }
      return input;
    };

    /** Runs during page load.*/
      _loadClientConfig = function(formData){
        var valve_names = formData.params.split(",");
        valve_names = valve_names.map(s => s.trim());

        http.get("/viewclientconfig")
          .then(function(response){
            var nodeList = response.data.nodes.ids.split(' ');
            angular.forEach(nodeList, function(value) {
              if(valve_names.indexOf(response.data[value].name) > -1) {
                $scope.editFormData.ValveDetails.push(
                  {
                    id: response.data[value].id,
                    name: response.data[value].name,
                    selected:true
                  }
                );
              } else {
                $scope.editFormData.ValveDetails.push(
                  {
                    id: response.data[value].id,
                    name: response.data[value].name,
                    selected:false
                  }
                );
              }
            });
        });
      }

      _loadClientConfig(formData); 

    $scope.cancel = function () {
        $modalInstance.close('yes');
    };

}]); // end: controller:editScheduledController


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
