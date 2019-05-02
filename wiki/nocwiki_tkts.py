"""nocwiki_tkts is a script to generate ServiceNow tickets based off a CSV"""

# This is in the Nagios folder
import servicenow_email as SN


def chunks(l, size):
    """
    chunks takes a list and size and returns a generator that
    breaks the list into smaller chunks of the specified size
    """
    for i in range(0, len(l), size):
        yield l[i : i + size]


with open("nocwiki.csv", newline="\n") as csvfile:
    LINES = list(chunks(csvfile.readlines(), 10))
    for count, group in enumerate(LINES, 1):
        email = SN.SNEmail(
            "liberty@service-now.com", "bwilkes5@liberty.edu", "Wiki Updates"
        )

        for index, value in enumerate(group):
            group[index] = value.replace(",", " (Last updated: ").replace("\n", ")")

        email.setBody(
            "Wiki's to update:\n\n"
            + "\n".join(group)
            + "\n\n\nAssignment group: System Operations - OCC"
            + "\nRequested for: bwilkes5"
            + "\nItem: Add/Change/Remove Documentation"
            + "\nDue date: 2019-07-01 00:00:00"
        )
        # print(email.msg)

        # UNCOMMENT THIS TO SEND THE EMAILS
        # email.send()
        print("Sent email {0} of 200".format(count))
