//////////////////////////////////////////////////////////////////////
//
// filename: index.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////

// create bus for communication between vue instances
Vue.prototype.$bus = new Vue();


// const vars
var homeUrl = "/"

function submitModifiedItem(item, itemIndex, successCallback){

	var formattedItem = formatFrontendItemToBackendItem(item);
	
	axios.put(`/media-info-record/${itemIndex}`, formattedItem).then((response) => {
		successCallback();
	})
    .catch(err => {
    	console.log(err);
		console.log("Updating media info record failed.")
    });
}

function formatFrontendItemToBackendItem(frontendItem){
	
	//deal with formatting each blacklist term
	var formattedBlackListTerms = [];

	frontendItem.blacklistTerms.forEach((blacklistTerm) => {
		formattedBlackListTerms.push(blacklistTerm.content);
	});

	//deal with new a blacklist term, if it exists
	if(frontendItem.newPotentialBlacklistItem.content.length > 0){
		formattedBlackListTerms.push(frontendItem.newPotentialBlacklistItem.content);
	}

	var formattedItem = {
		"name": frontendItem.name.content,
		"typeSpecificData": {
			"latestSeason": Number(frontendItem.typeSpecificData.latestSeason.content),
			"latestEpisode": Number(frontendItem.typeSpecificData.latestEpisode.content)
		},
		"blacklistTerms": formattedBlackListTerms,
	};

	return formattedItem;
}


function addNewBlacklistTermToItemModel(item){

	var newBlacklistTerm = {
		edit: false,
		content: item.newPotentialBlacklistItem.content
	}

	item.blacklistTerms.push(newBlacklistTerm);
}


function loadMediaIndexJson() {
	axios.get(`/media-info-records`).then((response) => {

		var mediaInfoList = response.data["media"];

		mediaInfoList = formatBackendItemToFrontendItem(mediaInfoList);

		new Vue({
			el: '#mediaIndexContent',
			data() {
				return {
					content: mediaInfoList,
					modalVisible: false,
					confirmCloseModalFunction: null,
					modalText: null,
				}
			},
			mounted() {
				this.$bus.$on("new-item-added", (newItem, successCallback) => {
					this.content.push(newItem);
					this.content.sort(function(a, b) { 
						return a.name.content.localeCompare(b.name.content);
					});
					successCallback();
				});

				for(var i = 0; i < this.content.length; i++){

					contentItem = this.content[i];

					this.makeSimilarShowsRequest(contentItem);
				}
			},
			methods: {
				makeFieldEditable: function (field){
					field.edit = true;
				},
				confirmItemEdit: function (item, editedField, itemIndex){
					editedField.edit = false;
					submitModifiedItem(item, itemIndex, function(){});
				},
				deleteMediaInfoRecord: function (itemIndex) {
					axios.delete(`/media-info-record/${itemIndex}`).then((response) => {
						this.content.splice(itemIndex, 1);
					}).catch(function(){
						console.log("Deleting media info record failed.")
					});
				},
				removeBlacklistTerm: function (item, itemIndex, blacklistTermForRemoval){

					for (var i = item.blacklistTerms.length - 1; i >= 0; i--) {
						var blacklistTerm = item.blacklistTerms[i];
						if(blacklistTerm.content == blacklistTermForRemoval.content){
							item.blacklistTerms.splice(i, 1);
							submitModifiedItem(item, itemIndex, function(){});
							break;
						}
					}

				},
				showModal: function(confirmFunction, modalText){
					this.modalText = modalText;
					this.modalVisible = true;
					this.confirmCloseModalFunction = confirmFunction;
				},
				confirmCloseModal: function(){
					this.modalVisible = false;
					this.confirmCloseModalFunction();
				},
				cancelCloseModal: function(){
					this.modalVisible = false;
				},
				addNewBlacklistTerm: function(item, itemIndex){
					submitModifiedItem(item, itemIndex, function(){
						addNewBlacklistTermToItemModel(item);
						item.newPotentialBlacklistItem.edit = false;
						item.newPotentialBlacklistItem.content = "";
					});
				},
				addSimilarShow: function(similarShow){

					var newItem = {
						mediaName: similarShow.content,
						latestSeason: "1",
						latestEpisode: "1",
						blacklistTerms: ""
					};
					var vueInstance = this;

					makeNewMediaInfoRecordCall(newItem, vueInstance, function () {}, function () {});
				},
				makeSimilarShowsRequest: function(contentItem){
					axios.get(`/similar-shows/${contentItem.name.content}`).then((response) => {
						contentItem.similarShows = addEditFieldToStringList(response.data["similarShows"]);
					});
				}
			}
		});
	});
}


function addEditFieldToObject(obj, relevantKey){

	var newObj = {
		edit: false
	}
	newObj["content"] = obj[relevantKey];

	obj[relevantKey] = newObj;
}


function addEditFieldToStringList(list){

	const newList = []

	list.forEach(function(item){
		var newObj = {
			edit: false
		}
		newObj["content"] = item;
		newList.push(newObj);
	});
	return newList;
}


function formatBackendItemToFrontendItem(mediaInfoData) {
	mediaInfoData.forEach(item => {
		Object.keys(item).forEach(key => {
			if(typeof item[key] === 'object'){
				var subItem = item[key];
				Object.keys(subItem).forEach(subKey => {
					addEditFieldToObject(subItem, subKey);
				});				
			}
			else{
				addEditFieldToObject(item, key);
			}			
		});

		item["newPotentialBlacklistItem"] = {
			edit: false,
			content: ""
		}
		item["newPotentialSimilarShowItem"] = {
			edit: false,
			content: ""
		}
		item["similarShows"] = [];

	});
	return mediaInfoData;
}


// register modal component
Vue.component("modal", {
	template: "#modal-template",
	methods:{
		okCloseModal: function(){
			console.log("Ok");
		},
		cancelCloseModal: function(){
			console.log("cancel");
		}
	}
});


function makeNewMediaInfoRecordCall(newItem, vueInstance, successCallback, errorCallback){
	axios.post(`/media-info-record/0`, newItem).then((response) => {

		var newFrontendItem = formatBackendItemToFrontendItem([{
			"name": newItem.mediaName,
			"typeSpecificData": {
				"latestSeason": newItem.latestSeason,
				"latestEpisode": newItem.latestEpisode
			},
			"blacklistTerms": newItem.blacklistTerms
		}])[0];

		vueInstance.$bus.$emit("new-item-added", newFrontendItem, function () {
			successCallback(response);
		});

	}).catch(function (response) {
		errorCallback(response);
	});
}



// js execute section
loadMediaIndexJson();