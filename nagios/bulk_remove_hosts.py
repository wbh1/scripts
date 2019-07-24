import urllib3
import requests

# !!! Change this !!!
APIKEY = "API_KEY_GOES_HERE_YA_DINGUS"

HOSTS = (
    """
ws406-ste406.university.liberty.edu
ws412-ste412.university.liberty.edu
ws411-ste411.university.liberty.edu
ws410-ste410.university.liberty.edu
ws409-ste409.university.liberty.edu
ws408b-ste408b.university.liberty.edu
ws407-ste407.university.liberty.edu
ws408a-ste408a.university.liberty.edu
ws406-ste406.university.liberty.edu
ws405-ste405.university.liberty.edu
ws404-ste404.university.liberty.edu
ws119-cn1.university.liberty.edu
ws119-cn2.university.liberty.edu
ws401-ste401.university.liberty.edu
ws402-ste402.university.liberty.edu
ws414-ste414.university.liberty.edu
ws413-ste413.university.liberty.edu
ws415-ste415a.university.liberty.edu
ws415-ste415b.university.liberty.edu
ws416-ste416.university.liberty.edu
ws403-ste403.university.liberty.edu
foc214_blu80.audio-dsp.media-systems.liberty.edu
foc213_blu80.audio-dsp.media-systems.liberty.edu
"""
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    for host in HOSTS.split("\n"):
        # Make sure it's not an empty line
        if host:
            PARAMS = [
                ("apikey", APIKEY)]
            PARAMS.append(("host_name", host))

            response = requests.delete(
                "https://nagios.liberty.edu/nagiosxi/api/v1/config/host",
                params=PARAMS,
                verify=False
            )

            print(response.json())
