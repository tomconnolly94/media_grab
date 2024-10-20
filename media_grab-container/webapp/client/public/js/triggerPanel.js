//////////////////////////////////////////////////////////////////////
//
// filename: torrentTitlePanel.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////



new Vue({
	el: '#triggerPanel',
	data() {
		return {
			responseMessage: "",
			running: false,
			startTime: null,
			originalSpinnerParentClass: "col-sm-6 col-xl-4",
			spinnerParentClass: this.originalSpinnerParentClass
		}
	},
	methods: {
		cleanUpMediaGrabRun: function(success){
			var successStr = success ? "successfully" : "unsuccessfully";
			console.log(`runMediaGrab finished ${successStr}.`);
			this.responseMessage = `MediaGrab run ${successStr} at ${vueComponent.startTime}`
			this.running = false;
			this.spinnerParentClass = this.originalSpinnerParentClass
		},
		runMediaGrab: function (){
			if (this.running){
				return;
			}

			this.running = true;
			this.startTime = new Date().toLocaleString();
			this.spinnerParentClass = "col-sm-8"
			this.responseMessage = "";
			vueComponent = this;

			axios.get(`/run-media-grab`).then((response) => {
				vueComponent.cleanUpMediaGrabRun(true);
			}).catch(function(){
				vueComponent.cleanUpMediaGrabRun(false);
			});
		}
	}
});
