//////////////////////////////////////////////////////////////////////
//
// filename: inputPanel.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////




new Vue({
	el: '#inputPanel',
	data() {
		return {
			mediaName: "",
			latestSeason: 1,
			latestEpisode: 1,
			blacklistTerms: "",
			errorMessage: ""
		}
	},
	methods: {
		submitNewMediaInfoRecord: function (){
			var newRecordForm = document.newMediaInfoRecord;

			console.log(`Adding new mediaInfoRecord from form=${newRecordForm}`);
			// extract data
			var blacklistTerms = this.blacklistTerms.length > 0 ? this.blacklistTerms.split(/[\n,]+/) : [];
		
			var newItem = {
				mediaName: this.mediaName,
				latestSeason: this.latestSeason,
				latestEpisode: this.latestEpisode,
				blacklistTerms: blacklistTerms.join()
			};

			console.log(`newItem=${newItem}`);

			var vueComponent = this;

			makeNewMediaInfoRecordCall(newItem, vueComponent, function(response){
				vueComponent.resetForm();
			}, function(error){
				let errorResponse = error.response.data;
				let message = `Adding media info record failed: ${errorResponse}`;
				console.log(message);
				vueComponent.errorMessage = message;
			});
		},
		resetForm: function () {
			var newRecordForm = document.newMediaInfoRecord;

			//clear fields
			newRecordForm[0].value = "";
			newRecordForm[1].value = "";
			newRecordForm[2].value = "";
			newRecordForm[3].value = "";
		},
		checkTorrentTitles: function () {
			Vue.prototype.$bus.$emit("checkTorrentTitles", document.newMediaInfoRecord[0].value);
		}
	}
});
