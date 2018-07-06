var occTeams = new TeamsMessage();
var occSlack = new SlackMessage2();


// Initial variable declarations
var title = ":globe_with_meridians: " + current.number.toString();
var titlelink = "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=" + current.sys_class_name + ".do?sys_id=" + current.sys_id;

// need pretext to be global variable instead of local
pretext = "if you see this, bad luck on you";

changeCondition = 0; // 1 = Closed, 2 = Updated, 3 = assignment group change, 4 = priority updated

// conditionally set the title of the card
function whatChanged() {
    if (current.active.changesTo('true')) {
        pretext = "New Incident Assigned";
    } else if (current.active.changesTo('false')) {
        pretext = "Incident Closed";
        changeCondition = 1;
        occTeams.payload.sections.push({
            "text": "## Close Notes: \r\n" + " " + current.close_notes.toString()
        });
    } else if (current.comments.changes()) {
        pretext = "Incident Updated";
        changeCondition = 2;
        occTeams.payload.sections.push({
            "text": "## Comments: \r\n" + " " + current.comments.toString()
        });
    } else if (current.assignment_group.changes()) {
        pretext = "Incident Assignment Group Changed";
        changeCondition = 3;
        occTeams.payload.text = "New Assignment Group: _" + current.assignment_group.name + "_";
    } else if (current.priority.changes()) {
        pretext = "Incident Priority Updated";
        changeCondition = 4;
    } else {
        pretext = "New Incident Assigned";
    }
}

// The facts displayed at the top of the card
function headerSet() {

    ///////////////////////////// TEAMS /////////////////////////////
    occTeams.payload.title = pretext;
    occTeams.payload.sections.length = 0;
    occTeams.payload.sections.unshift({
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

    ///////////////////////////// SLACK /////////////////////////////
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

    if (changeCondition == 1) {
        updatedBy();
        fields.titles.push("Close Notes");
        fields.values.push(current.close_notes.toString());
        fields.isitshort.push(0);
    } else if (changeCondition == 2) {
        updatedBy();
        fields.titles.push("Additional Comments");
        fields.values.push(current.comments.toString());
        fields.isitshort.push(0);
    } else if (changeCondition == 3) {
        updatedBy();
        fields.values[1] = current.assignment_group.name + "\n(was: " + previous.assignment_group.name + ")";
    } else if (changeCondition == 4) {
        updatedBy();
        fields.values[3] = current.priority.toString() + "(was: " + previous.priority.toString() + ")";
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

// send the message........
function sendIt() {
    ///////////////////////////// TEAMS /////////////////////////////
    // Subtitle of the card
    occTeams.payload.text = "Assigned to: _" + current.assignment_group.name + "_";

    // add the link to the open the card in ServiceNow
    occTeams.payload.potentialAction.length = 0;
    occTeams.payload.potentialAction.push({
        "@type": "OpenUri",
        "name": "Open in ServiceNow",
        "targets": [{
            "os": "default",
            "uri": titlelink
        }]
    });
    occTeams.send('TEAMSURLGOESHERE');

    ///////////////////////////// SLACK /////////////////////////////
    var slackurl = "SLACKURLGOESHERE";
    occSlack.send(slackurl);
}

///////////////// The Money //////////////////////
whatChanged();
headerSet();
sendIt();