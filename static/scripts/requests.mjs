export {makeGetRequest, makePostRequest};
/**
* HTTP GET request 
* @param  {string}   url       URL path, e.g. "/api/allprofs"
* @param  {function} onSuccess   callback method to execute upon request success (200 status)
* @param  {function} onFailure   callback method to execute upon request failure (non-200 status)
* @return {None}
*/

// with your backend.
var apiUrl = 'http://localhost:5000';
//var apiUrl = 'http://ta_management.herokuapp.com';

var makeGetRequest = function makeGetRequest(url, onSuccess, onFailure) {
    $.ajax({
        type: 'GET',
        url: apiUrl + url,
        dataType: "json",
        success: onSuccess,
        error: onFailure
    });
}


/**
 * HTTP POST request
 * @param  {string}   url       URL path, e.g. "/api/allprofs"
 * @param  {Object}   data      JSON data to send in request body
 * @param  {function} onSuccess   callback method to execute upon request success (200 status)
 * @param  {function} onFailure   callback method to execute upon request failure (non-200 status)
 * @return {None}
 */
var makePostRequest = function(url, data, onSuccess, onFailure) {
    $.ajax({
        type: 'POST',
        url: apiUrl + url,
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",
        success: onSuccess,
        error: onFailure
    });
}