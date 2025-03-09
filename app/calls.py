from app import db
from app.models import CallRecord as CallRecordModel
from datetime import datetime
import requests as rq
import base64


AIRCALL_URL = "https://api.aircall.io/v1"
SPEECHFLOW_URL = "https://api.speechflow.io/asr/file/v1"


class CallHelper:
    aircall_token = None

    def __init__(self, existingClient):
        s = existingClient.aircall_id+":"+existingClient.aircall_key
        byteS = s.encode(encoding="utf-8")
        self.aircall_token = base64.b64encode(byteS)

    def check_connection(self):
        headers = {"Authorization": b"Basic "+self.aircall_token}
        res = rq.get(AIRCALL_URL+"/ping", headers=headers)
        return res.status_code == 200

    def get_calls(self, existingCampaign):
        headers = {"Authorization": b"Basic "+self.aircall_token}
        start = f"{datetime.combine(existingCampaign.start_date, datetime.min.time()).timestamp}"
        if existingCampaign.end_date:
            end = f"{datetime.combine(existingCampaign.end_date, datetime.min.time()).timestamp}"
        else:
            end = datetime.now().timestamp()
        params = {
            "from": start,
            "to": end,
            "per_page": 50,
            "order": "desc"
        }
        res = rq.get(AIRCALL_URL+"/calls/search", headers=headers, params=params)
        return res.json()

    def filter_calls(self, calls, leads):
        leads_number = [lead.phone for lead in leads]
        filtered_calls = []
        for call in calls:
            # if the call id is in the database then skip that call.
            q = (
                db.select(CallRecordModel)
                .where(CallRecordModel.call_id == call["id"])
            )
            existingCall = db.session.scalar(q)
            if existingCall:
                continue
            if call["raw_digits"] in leads_number:
                filtered_calls.append(call)
        # Filter calls raw_digit to check if it matches with any of the leads.
        return filtered_calls

    def get_call_transcription(self, call):
        headers = {"Authorization": b"Basic "+self.aircall_token}
        # Get the calls transcription from aircall.
        print(f"Call id is {call['id']}")
        res = rq.get(AIRCALL_URL+f"/calls/{call['id']}/transcription", headers=headers)
        # Check if the participant_type is external then add lead before the text.
        if not res.status_code == 200:
            print("calls.py| l:64", res.json(), res.status_code)
            if res.status_code == 404:
                return "Transcription is not available for this call"
            return "Error in getting transcription"
        transcription = ""
        data = res.json()
        for utterances in data['transcription']['content']["utterances"]:
            # Check if the participant_type is internal then add agency before the text.
            prefix = "Lead: " if utterances['participant_type'] == "external" else "Agency: "
            # add line break after every loop of utterances
            transcription += f"{prefix} {utterances['text']} \n"
        return transcription

    def convert_date(self, date):
        return datetime.utcfromtimestamp(int(date))
