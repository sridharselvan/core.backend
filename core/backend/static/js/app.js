
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

//Start: Alert Message
app.controller('messageController', ['$scope', '$timeout', '$modalInstance', 'msgData', function($scope, $timeout, $modalInstance, msgData){

  $scope.errorMsg = msgData;
  $timeout(function(){
    $modalInstance.close('yes');
  }, 2000);

  $scope.cancel = function(){
    $modalInstance.close('yes');
  }

}]);
//End: Alert Message


//Start: controller: LogoutController
app.controller('menuController',['$scope', 'http', '$state', '$stateParams', '$timeout', '$rootScope', '$modal', function($scope, http, $state, $stateParams, $timeout, $rootScope, $modal){

    $scope.logout = function(){

      if(confirm('Are you sure you want to logout this?')){
        http
          .get('/logoutuser')
          .then(function(response) {
            $state.transitionTo('logout');
        });
      }
    };

  $scope.alertMessage = function(msg) {
    var modalInstance = $modal.open({
      templateUrl: 'alert-message.html',
      controller: 'messageController',
      backdrop: "static",
      backdropClick: false,
      resolve: {
         msgData: function () {
           return msg;
         }
       },
       size: 'sm'
    });
  }

  $rootScope.$on('alert', function (event, args) {
   $scope.alertMessage(args.msg);
  });
  
}]); //End: controller: LogoutController

//Start: controller: LogoutController
app.controller('logoutController', function($scope, http, $state, $stateParams){

  $scope.session_valid = $stateParams['session_valid'];
  
}); //End: controller: LogoutController


//Start: controller:clientConfigController
app.controller("clientConfigController", function($scope, http, $state, $rootScope) {

    /** Runs during page load.*/
    _loadClientConfig = function(){
      http.get("/viewclientconfig")
        .then(function(response){
          $scope.serverData = response.data;
      });
    }

    _loadClientConfig();

    //Toggle
    $scope.toggleHrsMins = function(duration_type, node){
      return (duration_type == 'Mins') ? 'Hrs' : 'Mins';
    }

    //Save/update the form data to client ini fiile
    $scope.saveConfig = function () {

      http.post("/modifyclientconfig", $scope.serverData)
        .then(function(response){
          $scope.serverData = response.data;
          $rootScope.$emit('alert', {msg:'Data saved successfully'});
          _loadClientConfig();
      });
    };

    //Toggle glyphicon
    $scope.toggleNodes = function(active, span_id){
      var add_class_name = (active) ? 'glyphicon-chevron-down':'glyphicon-chevron-right',
      remove_class_name = (active) ? 'glyphicon-chevron-right':'glyphicon-chevron-down';
      angular.element('#node-config-'+span_id).removeClass(remove_class_name);
      angular.element('#node-config-'+span_id).addClass(add_class_name);
    }

}); // end: controller:clientConfigController

//Start: controller:schedulerController
app.controller("schedulerController",['$scope', 'http', '$state', '$filter', '$window', '$modal', '$rootScope', '$timeout',
  function($scope, http, $state, $filter, $window, $modal, $rootScope, $timeout) {

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
    
    //Resetting the error message flag
    $scope.frequencyMsg = false;
    $scope.weekDayMsg = false;
    $scope.valveMsg = false;

    var max = ($scope.schedulerData.type.toLowerCase() == 'weekly') ? 5 : 31;
    $scope.schedulerData.recurs = [];
    for(var i=1;i<=max;i++){
      var j = (i<10) ? '0'+i : i;
      $scope.schedulerData.recurs.push({id:i, value:j, selected:false});
    };
    $scope.schedulerData.start_date.day = $filter('date')(new Date(), 'dd');
    $scope.schedulerData.start_date.month = $filter('date')(new Date(), 'MM');
    $scope.schedulerData.start_date.year = $filter('date')(new Date(), 'yyyy');
    $scope.schedulerData.start_date.hour = $filter('date')(new Date(), 'HH');
    $scope.schedulerData.start_date.mins = $filter('date')(new Date(), 'mm');
  };

  $scope.selectAllDays = function(isAllDays){
    var frequency = $scope.schedulerData.recurs;
    for(var i=0;i<frequency.length;i++){
      $scope.schedulerData.recurs[i]['selected'] = isAllDays;
    }
  };

  $scope.selectAllWeekDays = function(isAllWeekDays){
    var weekDays = $scope.schedulerData.weekDays;
    for(var i=0;i<weekDays.length;i++){
      $scope.schedulerData.weekDays[i]['selected'] = isAllWeekDays;
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

  $scope.$on('eventName', function (event, args) {
   $scope.SearchScheduledJob();
  });

  //New scheduler form validation
  $scope.bandChoosed = function(object) {
    var trues = $filter("filter")(object, {
        selected: true
    });
    return trues.length;
  }

  $scope.triggerScheduler = function(){

    $scope.frequencyMsg = false;
    $scope.weekDayMsg = false;
    if($scope.schedulerData.type == 'Daily' || $scope.schedulerData.type == 'Weekly'){
      $scope.frequencyMsg = ($scope.bandChoosed($scope.schedulerData.recurs) <= 0) ? true : false;
    }
    if($scope.schedulerData.type == 'Weekly'){
      $scope.weekDayMsg = ($scope.bandChoosed($scope.schedulerData.weekDays) <= 0) ? true : false;
    }
    $scope.valveMsg = ($scope.bandChoosed($scope.schedulerData.ValveDetails) <= 0) ? true : false;
    if(!$scope.frequencyMsg && !$scope.valveMsg && !$scope.weekDayMsg){

      //Disabling the schedule button to avoid multiple click
      $scope.isScheduleDisable = true;
      http
        .post('/saveschedulerconfig', $scope.schedulerData)
        .then(function(response) {

          //Eabling the schedule button after response
          $scope.isScheduleDisable = false;
          //Emitting alert message
          $rootScope.$emit('alert', {msg:'Data saved successfully'});
          $scope.schedulerData.type = $scope.types[0];
          $state.go($state.current, {}, {reload: true});
      });
    }
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
        $rootScope.$emit('alert', {msg:'Deactivated successfully'});
    }); 
  };

  $scope.editScheduledJob = function(scheduledJob) {
    var modalInstance = $modal.open({
      templateUrl: 'edit-scheduled-event.html',
      controller: 'editScheduledController as editCtrl',
      backdrop: "static",
      backdropClick: false,
      //windowClass: 'xx-dialog',
      size: 'xl',
      resolve: {
         editData: function () {
           return scheduledJob;
         }
       },
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
app.controller("editScheduledController",['$scope', '$modalInstance', 'editData', 'http', '$state', '$rootScope', '$filter',
  function($scope, $modalInstance, editData, http, $state, $rootScope, $filter) {

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

    //Edit scheduler form validation
    $scope.bandChoosed = function(object) {
      var trues = $filter("filter")(object, {
          selected: true
      });
      return (trues.length <= 0) ? true : false;
    };

    $scope.updateScheduler = function(){

      $scope.editFrequencyMsg = false;
      $scope.editWeekDayMsg = false;
      if($scope.editFormData.type == 'Daily' || $scope.editFormData.type == 'Weekly'){
        $scope.editFrequencyMsg = $scope.bandChoosed($scope.editFormData.recurs)
      }
      if($scope.editFormData.type == 'Weekly'){
        $scope.editWeekDayMsg = $scope.bandChoosed($scope.editFormData.weekDays)
      }
      $scope.editValveMsg = $scope.bandChoosed($scope.editFormData.ValveDetails)
      if(!$scope.editFrequencyMsg && !$scope.editValveMsg && !$scope.editWeekDayMsg){
        http
          .post('/updateschedulerconfig', $scope.editFormData)
          .then(function(response) {
            $rootScope.$broadcast('eventName', {});
            $modalInstance.close('yes');
        });
      };
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
              var session_valid = (response.data.is_session_valid == false) ? true: false;
              if(response.data.is_session_valid){
                deferred.resolve(response);
              } else {
                $state.go('logout',{session_valid: session_valid});
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
              $state.go('logout',{session_valid: ressession_valid});
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
    params: {session_valid:null},
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
