import ApiCalls from "./api_calls"


class EventLogger {
	constructor(logServerUrl) {
		this.api = new ApiCalls(logServerUrl);
	}
	
	commonHeaders = { "Content-Type": "application/json" };
	
	getAuthHeaders() {
		let authHeaders = {
			"EVL-USER-API-KEY" : "token",
		}
		return Object.assign({}, this.commonHeaders, authHeaders);
	}
	
	checkNetworkConnectionStatus(speed = false) {
		let status = true;
		let online = window.navigator.onLine;
		if (!online) {
			status = false;
		} 

		if (speed) {
			status = window.navigator.connection.downlink;
		}

		return status;
	}

	logEvent(log_tag, log_data_type, log = undefined, log_data = undefined) {
		let allowedDataType = ["data","text"];

		if (!allowedDataType.includes(log_data_type)) {
			console.error("log_data_type should be one of "+allowedDataType)
			return;
		}

		let that = this;
		let payload = {
			"log_type" : log_data_type,
			"data" : log_data,
			"text" : log,
			"log_tag" : log_tag,
			"client_info" : {
				"nwspeed" : that.checkNetworkConnectionStatus(true)
			}
		}

		this.api.postData("/log/"+log_tag, this.getAuthHeaders(), [], payload, function(response) {
			if (!response.status) {
				console.error(response);
				console.error("Posting logs failed.");
			} else {
				console.log("Log Posted successfully.");
			}
		})
	}

	log(log_tag, log_text) {
		this.logEvent(log_tag, "text", log_text);
	}

	logData(log_tag, log_text, log_data) {
		this.logEvent(log_tag, "data", log_text, log_data);
	}
}

export default EventLogger