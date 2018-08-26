var occTeams = new TeamsMessage();
var occSlack = new SlackMessage2();

///////////////////////////// SHARED DEFAULTS /////////////////////////////

var title = ":globe_with_meridians: " + current.number.toString();
var titlelink = "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=" + current.sys_class_name + ".do?sys_id=" + current.sys_id;
var pretext = "if you see this, bad luck on you";
var changeCondition = 0; // 0 = New/default, 1 = Closed, 2 = Updated, 3 = assignment group change, 4 = priority updated

function defaultsChange() {
    switch (changeCondition) {
        case 1:
            pretext = "Incident Closed";
            break;
        case 2:
            pretext = "Incident Updated";
            break;
        case 3:
            pretext = "Incident Assignment Group Changed";
            break;
        case 4:
            pretext = "Incident Priority Updated";
            break;
        default:
            pretext = "New Incident Assigned";
            break;
    }
}

// Set Card Title Based on What Changed
function whatChanged() {
    if (current.active.changesTo('true')) {
        pretext = "New Incident Assigned";
    } else if (current.active.changesTo('false')) {
        changeCondition = 1;
	} else if (current.comments.changes()) {
        changeCondition = 2;
	} else if (current.assignment_group.changes()) {
        changeCondition = 3;
	} else if (current.priority.changes()) {
        changeCondition = 4;
	} else {
        // if nothing changed, default to it being a new INC
        pretext = "New Incident Assigned";
    }
}

///////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////// TEAMS ////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////


// The facts displayed at the top of the Teams card
function teamsHeaderSet () {
	occTeams.payload.text = "Assigned to: _" + current.assignment_group.name + "_";
    occTeams.payload.title = pretext;
    occTeams.payload.sections.length = 0;
    
	occTeams.payload.sections.push({
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

function teamsBodySet() {
    switch (changeCondition) {
        case 1:
            occTeams.payload.sections.push({
            "title": "## Close Notes",
            "text": current.close_notes.toString()
            });
            break;
        case 2:
            occTeams.payload.sections.push({
            "title": "## Additional Comments",
            "text": current.comments.toString()
            });
            break;
        case 3:
            occTeams.payload.text = "Assigned to: _" + current.assignment_group.name + "_ (was: " + previous.assignment_group.name + ")";
            break;
        case 4:
            occTeams.payload.sections[0].facts[2].value = current.priority.toString() + " (was: " + previous.priority.toString() + ")";
            break;
    }
}

function teamsSend() {
	occTeams.payload.potentialAction.length = 0;
	occTeams.payload.potentialAction.push({
		"@type": "OpenUri",
			   "name": "Open in ServiceNow",
			   "targets": [
					{ "os": "default", "uri": titlelink }]
	});
	// occTeams.send('https://outlook.office.com/webhook/ff8b12f1-629c-452d-9991-9da18589836d@baf8218e-b302-4465-a993-4a39c97251b2/IncomingWebhook/cc87a04113744581896791c021ec9333/91bbe1c0-a46d-4ac4-a55c-ce0cee42b232');
	occTeams.send('https://outlook.office.com/webhook/ff8b12f1-629c-452d-9991-9da18589836d@baf8218e-b302-4465-a993-4a39c97251b2/IncomingWebhook/d7f1650cc8ec4143aa8321b7bda74b35/91bbe1c0-a46d-4ac4-a55c-ce0cee42b232');

}



///////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////// SLACK ////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////

    
function slackHeaderSet() {
    var fields = {
        titles: ["Short Description", "Assignment Group", "Requested for", "Priority"],
        values: [current.short_description.toString(), current.assignment_group.getDisplayValue(), current.caller_id.getDisplayValue(), current.priority.toString()],
        isitshort: [0, 1, 1, 1]
    };

    function updatedBy() {
        fields.titles.push("Updated by");
        fields.values.push(current.sys_updated_by.toString());
        fields.isitshort.push(1);
    }
    switch (changeCondition) {
        case 1:
            updatedBy();
            fields.titles.push("Close Notes");
            fields.values.push(current.close_notes.toString());
            fields.isitshort.push(0);
            break;
        case 2:
            updatedBy();
            fields.titles.push("Additional Comments");
            fields.values.push(current.comments.toString());
            fields.isitshort.push(0);
            break;
        case 3:
            updatedBy();
            fields.values[1] = current.assignment_group.name + "\n(was: " + previous.assignment_group.name + ")";
            break;
        case 4:
            updatedBy();
            fields.values[3] = current.priority.toString() + "(was: " + previous.priority.toString() + ")";
            break;
    }

    var slackFields = [];

    for (i = 0, len = fields.titles.length; i < len; i++) {
        slackFields.push({
            "title": fields.titles[i],
            "value": fields.values[i],
            "short": fields.isitshort[i]
        });
    }

    occSlack.payload.attachments.push({
        "title": title,
        "title_link": titlelink,
        "pretext": pretext,
		"fallback": pretext,
		"color": "#36a64f",
		"fields": slackFields,
    });
}

function slackSend() {
    occSlack.send('https://hooks.slack.com/services/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');
    // occSlack.send('https://hooks.slack.com/services/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');

}

///////////////// The Money //////////////////////
whatChanged();
defaultsChange();
teamsHeaderSet();
teamsBodySet();
slackHeaderSet();
teamsSend();
slackSend();