var SlackMessage2 = Class.create();
 
SlackMessage2.prototype = {
    initialize : function() {
    },
     
    'send': function (endpoint) {
        // Set the text and channel (or fall back to defaults)
        this.endpoint = endpoint;
        // Encode the payload as JSON
        var SNJSON = JSON; // Workaround for JSLint warning about using JSON as a constructor
        var myjson = new SNJSON();
        var encoded_payload = myjson.encode(this.payload);
         
		// Create and send the REST Message
		var msg = new sn_ws.RESTMessageV2();
		msg.setEndpoint(this.endpoint);
		msg.setHttpMethod(this.method);
		msg.setRequestBody(encoded_payload);
		var res = msg.execute();
		return res;
    },
    'endpoint': '',
    'method': 'post',
    'payload': {
        'text': '',
        'attachments': []
    },
     
    'type': 'SlackMessage2'
};