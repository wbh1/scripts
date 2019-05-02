function doThings() {
  IncCommTeams = new TeamsMessage();

  IncCommTeams.payload.sections.length = 0;

  // The facts displayed at the top of the card
  IncCommTeams.payload.sections.push({
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

  // conditionally set the title of the card
  if (current.active.changesTo('true')) {
    IncCommTeams.payload.title = "New Incident Assigned";
    sendIt(IncCommTeams);
  } else if (current.active.changesTo('false')) {
    IncCommTeams.payload.title = "Incident Closed";
    IncCommTeams.payload.sections.push({
      "text": "## Close Notes: \r\n" + " " + current.close_notes.toString()
    });
    sendIt(IncCommTeams);
  } else if (current.priority.changes()) {
    IncCommTeams.payload.title = "Incident Priority Updated";
    sendIt(IncCommTeams);
  } else if (current.assignment_group.changes()) {
    IncCommTeams.payload.title = "Incident Assignment Group Changed";
    IncCommTeams.payload.text = "New Assignment Group: _" + current.assignment_group.name + "_";
    sendIt(IncCommTeams);
  }
}

// send the message........
function sendIt(IncCommTeams) {
  // Subtitle of the card
  IncCommTeams.payload.text = "Assigned to: _" + current.assignment_group.name + "_";

  IncCommTeams.payload.potentialAction.length = 0;

  // add the link to the open the card in ServiceNow
  IncCommTeams.payload.potentialAction.push({
    "@type": "OpenUri",
    "name": "Open in ServiceNow",
    "targets": [
      { "os": "default", "uri": "https://" + gs.getProperty('instance_name') + ".service-now.com/nav_to.do?uri=incident.do?sys_id=" + current.sys_id }]
  });
  IncCommTeams.send(URL_GOES_HERE);
}

if (gs.getProperty('instance_name') == "liberty"){
  doThings();
}