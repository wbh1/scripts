var notifychannel = new TeamsMessage();
var testingchannel = new TeamsMessage();
var SN_link = "https://" + gs.getProperty('instance_name') + ".service-now.com/change_request.do?sys_id=" + current.sys_id;

// The facts displayed at the top of the card
notifychannel.payload.sections.length = 0;
notifychannel.payload.sections.push({
    "facts": [{
        "name": "Change #:",
        "value": current.number.toString()
    }],
    "markdown": true
});

testingchannel.payload.sections.length = 0;
testingchannel.payload.sections.push({
    "facts": [{
        "name": "Change #:",
        "value": current.number.toString()
    }],
    "markdown": true
});

// conditionally set the title of the card
if (current.active.changesTo('true')) {
    sendBoth();
} else if (current.active.changesTo('false')) {
    sendNotify("closed");
}


// send the message........
function sendNotify(state) {
    // Subtitle of the card
    if (state == "open") {
        notifychannel.payload.title = "New Monitoring Standard Change";
    } else if (state == "closed") {
        notifychannel.payload.title = "Standard Monitoring Change Closed";
    }
    
    notifychannel.payload.text = "Assigned to: _" + current.assignment_group.name + "_";

    // add the link to the open the card in ServiceNow
    notifychannel.payload.potentialAction.push({
        "@type": "OpenUri",
        "name": "Open in ServiceNow",
        "targets": [{
            "os": "default",
            "uri": SN_link
        }]
    });
    notifychannel.send('https://outlook.office.com/webhook/216f1f97-3864-41ee-8f8c-2da7a4fa260e@baf8218e-b302-4465-a993-4a39c97251b2/IncomingWebhook/e351a25534af46828a34846b4f153df5/91bbe1c0-a46d-4ac4-a55c-ce0cee42b232');
}

function sendTesting() {

    var inputDate = new GlideDateTime();
    var initialDateTimeFormat = new Packages.java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    var initialFormattedDate = initialDateTimeFormat.parse(inputDate);
    var finalDatetimeFormat = new Packages.java.text.SimpleDateFormat("MMMM dd, yyyy");
    var date = finalDatetimeFormat.format(initialFormattedDate);

    testingchannel.payload.title = "Testing Nagios Configuration Coordination";
    testingchannel.payload.text = "Test Config applications for " + date;

    // add the link to the open the card in ServiceNow
    testingchannel.payload.potentialAction.length = 0;
    testingchannel.payload.potentialAction.push({
        "@type": "OpenUri",
        "name": "Open in ServiceNow",
        "targets": [{
            "os": "default",
            "uri": SN_link
        }]
    });
    testingchannel.send('https://outlook.office.com/webhook/216f1f97-3864-41ee-8f8c-2da7a4fa260e@baf8218e-b302-4465-a993-4a39c97251b2/IncomingWebhook/5fc24ba08c344c4bbea09a83ce91df94/91bbe1c0-a46d-4ac4-a55c-ce0cee42b232');
}

function sendBoth() {
    sendNotify("open");
    sendTesting();
}