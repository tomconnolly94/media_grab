//////////////////////////////////////////////////////////////////////
//
// filename: torrentTitlePanel.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////



new Vue({
	el: '#torrentTitlePanel',
	data() {
		return {
			torrentTitles: [],
			showPanel: false
		}
	},
	beforeMount() {
		let vueComponent = this;
		Vue.prototype.$bus.$on('checkTorrentTitles', (searchTerm) => {
			vueComponent.getTorrentTitles(searchTerm);
		});
	},
	methods: {
		getTorrentTitles(searchTerm) {
			axios.get(`/torrent-titles/${searchTerm}`).then((response) => {
				console.log(response.data);
				this.torrentTitles = response.data.torrentTitles;
				console.log(this.torrentTitles);
				this.showPanel = true;
			}).catch(function () {
				this.torrentTitles = "woops";
			});
		},
		clearTorrentTitles(){
			this.torrentTitles = [];
			this.showPanel = false;
		}
	}
});