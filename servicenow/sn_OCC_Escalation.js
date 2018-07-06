// Did priority or escalation change?
function whatChanged() {
	
	if (current.priority.changes()) {
		prevPriority = previous.priority;
		newPriority = current.priority;

		// if the new priority is higher (therefore lower) than the old, then alert
		if (newPriority < prevPriority) {
			pretext = "A Ticket's Priority Has Been Raised";
		}
		else if (!prevPriority && newPriority <= 3) {   // !prevPriority checks for all sorts of null values
			pretext = "An Increased Priority TKT Has Been Assigned";
		}
		else {
			return false;
		}
	}
	else {
		pretext = "TKT Escalated by " + current.u_escalated_by.getDisplayValue();
	}
	
	// Proceed to the next step in the script
	tktDetails();
}

function tktDetails() {
	
	// Create the payload
	escalationMsg.payload.attachments.push({
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
	sendIt();
}

function sendIt() {
	var url = "SLACKURLGOESHERE";
	escalationMsg.send(url);
}


// Only run if this is on Prod
// This is to prevent alerts from scheduled templates that have increased priority
if (gs.getProperty('instance_name') == "liberty") {
    // Create message framework
    var escalationMsg = new SlackMessage2();

    // Initial variable declarations
    var title = ":globe_with_meridians: " + current.number.toString();
    var titlelink = "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=" + current.sys_class_name + ".do?sys_id=" + current.sys_id;

    // need pretext to be global variable instead of local
    pretext = "if you see this, bad luck on you";
    whatChanged();
}