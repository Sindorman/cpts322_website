import {makePostRequest} from "./requests.mjs";
export {login};
function login () {

    var login_form;
    var student_data;

    var loginHandler = function(e) {

        login_form.on('click', '.submit_user_input.btn-md.btn-primary', function (e) {
            e.preventDefault ();
            var login_info = {};
            login_info.userID = login_form.find('.login_box_form_name').val();
            login_info.pw = login_form.find('.login_box_form_password').val();
            var onSuccess = function(data) {
                location.replace('../viewprofile', data);
            };
            var onFailure = function(data) {
                if(data.status == "403"){
                    $('label#status_update').html('Sign in failed! Username or passoword do not match!');
                    $('label#status_update').css("color", "white");
                    return null;
                }
                alert("Sign in failed!");
                console.error("Sign in failed!");
            };

            makePostRequest('/api/login', login_info, onSuccess, onFailure);
            
        });
    };

    var updateLoginBox = function(data){
        var LogInBox = $(".login_box");
        LogInBox.html(data.data.name + " " + data.data.lastName);
    };

    var updateViewProfile = function(data){
        var user = data.data;
        var LogInInfo = $(".view_profile_columns");
        LogInInfo.find('.view_profile_information_name').html(user.name);
        LogInInfo.find('.view_profile_name').html("<h2>" + user.name + "<span>'s Profile</span></h2>");
    };

    var start = function() {
        login_form = $("form#login_box_form");
        loginHandler();
    };
    

    // PUBLIC METHODS
    // any private methods returned in the hash are accessible
    return {
        start: start
    };

};