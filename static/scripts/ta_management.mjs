import {makeGetRequest, makePostRequest} from "./requests.mjs";
export {ta_management};
function ta_management () {

    // PRIVATE VARIABLES
    var add_account; 

    // PRIVATE METHODS
    
    /**
     * Add event handlers for submitting the create review form.
     * @return {None}
     */
    var attachAccountHandler = function(e) {
        add_account.on('click', '.cancel', function (e) {
            //activate and show the #list tab
        });

        // TODO: The handler for the Post button in the form
        add_account.on('click', '.submit_user_input', function (e) {
            e.preventDefault ();
            var info = getContactInfo(add_account);
            var account_type = add_account.find('.account_type_input').val();
            info.password = add_account.find('.password_input').val();
            var onSuccess = function(data) {
                $('label#status_update').html('Account Successfully created');
                $('label#status_update').css("color", "grey");
            };
            var onFailure = function(data) {
                if(data.status == 409)
                    $('label#status_update').html('Account with this ' + data.responseJSON.reason + ' already exists');
                    $('label#status_update').css("color", "grey");
                    return null;
                alert("Failed to create new account!");
                console.error("Failed to create new account!"); 
            };

            makePostRequest('/api/new' + account_type.toLowerCase(), info, onSuccess, onFailure);
            
        });
    };

    /**
    * Grabs instructor's info.
    * @return {dict} // dictionary of student info
    */
    var getContactInfo = function(function_ref) {
        var contact = {};
        contact.name = function_ref.find('.firstname_input').val();
        contact.lastname = function_ref.find('.lastname_input').val();
        contact.ID = function_ref.find('.wsuID_input').val();
        contact.email = function_ref.find('.email_input').val();
        contact.phone = function_ref.find('.phone_input').val();

        return contact;
    };

    /**
    * Grabs student info.
    * @return {dict} // dictionary of student info
    */
    var getStudentInfo = function(data, function_ref) {
        data.major = function_ref.find('.major_input').val();
        data.gpa = function_ref.find('.gpa_input').val();
        data.experience = function_ref.find('.experience_input').val();

        return data;
    };

    /**
     * Start the app by displaying the list of the professors and attaching event handlers.
     * @return {None}
     */
    var start = function() {
        add_account = $("form#createAccountForm");
        attachAccountHandler();
    };
    

    // PUBLIC METHODS
    // any private methods returned in the hash are accessible
    return {
        start: start
    };
    
};
