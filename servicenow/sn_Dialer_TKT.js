// Create message framework
var dialerfailMsg = new SlackMessage2();

// Initial variable declarations
var title = ":globe_with_meridians: " + current.number.toString();
var titlelink = "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=" + current.sys_class_name + ".do?sys_id=" + current.sys_id;
var pretext = "New ServiceNow TKT for Dialer Issues";

function dialerDetails() {
	
	// Create the payload
	dialerfailMsg.payload.attachments.push({
        "title": title,
        "title_link": titlelink,
        "pretext": pretext,
		"fallback": pretext,
		"color": "#36a64f",
		"fields": [
			{
				"title": "Short Description",
				"value": current.short_description.toString()
			},
			{
				"title": "Requested for",
				"value": current.requested_for.getDisplayValue(),
				"short": true
			},
			{
				"title": "Priority",
				"value": current.priority.toString(),
				"short": true
			}
		],
    });
    // Send the message
    sendDialer();
}

function sendDialer() {
	var url = "SLACKURLGOESHERE";
	dialerfailMsg.send(url);
}

dialerDetails();