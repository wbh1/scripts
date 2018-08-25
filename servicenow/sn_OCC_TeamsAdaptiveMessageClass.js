var TeamsAdaptiveMessage = Class.create();

TeamsAdaptiveMessage.prototype = {
    initialize : function() {
    },
		// when you call teams.send() in your business rule, pass the endpoint in the parens
    'send': function (endpoint) {
        // Set the text and channel (or fall back to defaults)
        this.endpoint = endpoint;

        // Encode the payload as JSON
        var teamsSNJSON = JSON; // Workaround for JSLint warning about using JSON as a constructor
        var teamsmyjson = new teamsSNJSON();
        var teams_encoded_payload = teamsmyjson.encode(this.payload);

		// Create and send the REST Message
		var msg = new sn_ws.RESTMessageV2();
		msg.setEndpoint(this.endpoint);
		msg.setHttpMethod(this.method);
		msg.setRequestBody(teams_encoded_payload);
		var res = msg.execute();
		return res;
    },
    'endpoint': '',
    'method': 'post',
    'payload': {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.0",
        "body": [
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Incident Updated",
                        "weight": "bolder",
                        "size": "Large"
                    }
                ]
            },
            {
                "type": "Container",
                "items": []
            }
        ],
        "actions": []
    },

    'type': 'TeamsAdaptiveMessage'
};