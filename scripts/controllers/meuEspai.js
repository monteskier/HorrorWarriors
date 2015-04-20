'use strict';


angular.module('horrorWarriorApp')
  .controller('meuEspaiCtrl', function ($scope, $rootScope, $http) {
    $scope.nick = readCookie("nick");
    $scope.id = readCookie("id");
    var entrada = function(){ $http.post("../api/esMaster",{id:$scope.id}).
        success( function (data){
            data = JSON.parse(data);
            if(data["master"]==true){
                $scope.esMaster = true;
                $scope.esJugador = false;
            }else if(data["master"]==false){
                $scope.esMaster = false;
                $scope.esJugador = true;
            }
      }).error(function (data){

            console.log("Error de conexio a la prova del master");
      });
    };
    entrada();
  });
  