var monitoringMsg = new SlackMessage2();

// Initial variable declarations
var title = ":eyes: " + current.number.toString();
var titlelink = "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=" + current.sys_class_name + ".do?sys_id=" + current.sys_id;
pretext = "if you see this, bad luck on you";

function whatChanged() {
    if (current.active.changesTo('true')) {
        pretext = "New Monitoring Standard Change";
    } else if (current.active.changesTo('false')) {
        pretext = "Standard Monitoring Change Closed";
    }
    chgDetails();
}

function chgDetails() {
	
	// Create the payload
	monitoringMsg.payload.attachments.push({
        "title": title,
        "title_link": titlelink,
        "pretext": pretext,
		"fallback": pretext,
		"color": "#36a64f",
		"fields": [
			{
				"title": "Opened By",
                "value": current.short_description.toString(),
                "short": true
			},
			{
				"title": "Assignment group",
				"value": current.requested_for.getDisplayValue(),
				"short": true
			}
		],
    });
    // Send the message
    sendIt();
}

function sendIt() {
	var url = "SLACKURLGOESHERE";
	monitoringMsg.send(url);
}

whatChanged();