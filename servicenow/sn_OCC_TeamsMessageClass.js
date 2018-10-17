var TeamsMessage = Class.create();

TeamsMessage.prototype = {
    initialize : function() {
    },
		// when you call teams.send() in your business rule, pass the endpoint in the parens
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
         "@type": "MessageCard",
         "@context": "http://schema.org/extensions",
         "themeColor": "ff0000",
         "title": "<blank>",
         "text": "<blank>",
         "sections": [],
         "potentialAction": []
    },

    'type': 'TeamsMessage'
};