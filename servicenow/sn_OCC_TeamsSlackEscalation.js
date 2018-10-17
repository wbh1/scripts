var escalationTeams = new TeamsMessage();
var escalationSlack = new SlackMessage2();

///////////////////////////// SHARED DEFAULTS /////////////////////////////

var title = ":globe_with_meridians: " + current.number.toString();
var titlelink = "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=" + current.sys_class_name + ".do?sys_id=" + current.sys_id;
var pretext = "if you see this, bad luck on you";

// Set Card Title Based on What Changed
function whatChanged() {
	if (current.priority.changes()) {
		prevPriority = previous.priority;
		newPriority = current.priority;

		// if the new priority is higher (therefore lower) than the old, then alert
		if (newPriority < prevPriority) {
			pretext = "A Ticket's Priority Has Been Raised";
			return true;
		}
		else if (!prevPriority && newPriority <= 3) {   // !prevPriority checks for all sorts of null values
			pretext = "An Increased Priority TKT Has Been Assigned";
			return true;
		}
		else {
			return false;
		}
	}
	else {
		pretext = "TKT Escalated by " + current.u_escalated_by.getDisplayValue();
		return true;
	}
}

///////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////// TEAMS ////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////


// The facts displayed at the top of the Teams card
function teamsHeaderSet () {
	escalationTeams.payload.text = "Assigned to: _" + current.assignment_group.name + "_";
    escalationTeams.payload.title = pretext;
    escalationTeams.payload.sections.length = 0;
    
	escalationTeams.payload.sections.push({
		"facts": [{
					 "name": "Ticket #:",
					 "value": current.number.toString()
				 }, {
					 "name": "Short Description:",
					 "value": current.short_description.toString()
				 }, {
					 "name": "Priority:",
					 "value": current.priority.toString()
				 }, {
					 "name": "Updated by:",
					 "value": current.sys_updated_by.toString()
				 }],
      "markdown": true
    });
}


function teamsSend() {
	escalationTeams.payload.potentialAction.length = 0;
	escalationTeams.payload.potentialAction.push({
		"@type": "OpenUri",
			   "name": "Open in ServiceNow",
			   "targets": [
					{ "os": "default", "uri": titlelink }]
	});
	escalationTeams.send('url goes here');

}



///////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////// SLACK ////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////

    
function slackHeaderSet() {
	// Create the payload
	escalationSlack.payload.attachments.push({
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
}

function slackSend() {
    escalationSlack.send('url goes here');

}

///////////////// The Money //////////////////////
// Only run if this is on Prod
// This is to prevent alerts from scheduled templates that have increased priority
if (gs.getProperty('instance_name') == "liberty"){
	if(whatChanged()){
		teamsHeaderSet();
		slackHeaderSet();
		teamsSend();
		slackSend();
	}
}