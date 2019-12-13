var app = angular.module('notification',  []);
app.controller('cont1', function($scope, $http){
    $scope.update = false; 
    $http.get('/account/api').then(function(response){
        $scope.notifList = [];
        $scope.unreadList = [];
        $scope.limit = 30
        for(var i=0; i<response.data.length; i++){
            var notif={};
            notif.message = response.data[i].message;
            notif.datetime = response.data[i].datetime;
            notif.viewed =  response.data[i].viewed;
            notif.id =  response.data[i].id;
            if (response.data[i].viewed == false) {
                $scope.unreadList.push(notif);
            }
            $scope.notifList.push(notif);
        }
        $scope.count = $scope.unreadList.length
    });
});
app.controller('cont2', function($scope, $http) {
    $http.get('/unitmanagement/k9/api').then(function(response){
        $scope.k9List = [];
        for(var i=0; i<response.data.length; i++){
            var objs={};
            objs.id = response.data[i].id;
            objs.name = response.data[i].name;
            $scope.k9List.push(objs);
        }

        $scope.changedValue = function(item) {
            $scope.item = item
            $scope.handler = ''
            console.log($scope.item) 
            $scope.cap = ''
            $scope.userList = [];
            for(var i=0; i<response.data.length; i++){
               if (response.data[i].id == $scope.item){
                    $scope.cap = response.data[i].capability;
               }
            }

            $http.get('/unitmanagement/user/api').then(function(response){
                for(var i=0; i<response.data.length; i++){
                    var objs={};
                    if(response.data[i].capability== $scope.cap){
                        objs.id = response.data[i].id;
                        objs.fullname = response.data[i].fullname;
                        objs.capability = response.data[i].capability;
                        $scope.userList.push(objs);
                    }
                }
                console.log($scope.userList) 
            });

            $scope.changedValueUser = function(handler) {
                $scope.handler = handler
            }  

            $scope.reassign = function() {
                console.log($scope.item) 
                console.log($scope.handler) 

                var k9 = {partnered: true, handler:$scope.handler, id:$scope.item}
                var handler = {partnered: true, id:$scope.item}
                
                // $http.put('/unitmanagement/k9/api',k9)
                $http.save('/unitmanagement/k9/api', k9)
            }  

        }  

    });
});