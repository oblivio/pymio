var app = new Vue({
  el: '#app',
  props: ['download_list','search_results','isDownloading','isFinishedDownloading','isDownloadError'],
  data: {
    download_list: [],
    search_results: [],
    isFinishedDownloading:false,
    isDownloadError:false,
    isFinishedDownloading:false,
  },
  created: function () {
    this.checkYAML();
  },
  methods:{
    download_yaml:function(vid_id){
      if(app.isDownloading){
        //prevent double download
        return false;
      }
      app.isDownloading = true;
      fetch("/download_videos")
      .then( (response) => {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' +
              response.status);
            return;
          }


          response.json().then(function(data) {
            console.log('download yaml',data);
            app.isDownloading = false;
            app.isFinishedDownloading = true;
            setTimeout(()=>{
              app.isFinishedDownloading = false;
            },2000);
          });
        }
      )
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
        app.isDownloading = false;
        app.isDownloadError = true;
      });
    },
    removeVideo:function(vid_id){
      fetch("/set_yaml?vid_id="+vid_id+"&del=1")
      .then( (response) => {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' +
              response.status);
            return;
          }

          response.json().then(function(data) {
            console.log('update yaml',data);
            var button = document.getElementById("refresh-button")
            button.click();
          });
        }
      )
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
      });
    },
    addVideo:function(vid_id){
      fetch("/set_yaml?vid_id="+vid_id)
      .then( (response) => {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' +
              response.status);
            return;
          }


          response.json().then(function(data) {
            console.log('update yaml results',data);
            var button = document.getElementById("refresh-button")
            button.click();
          });
        }
      )
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
      });
    },
    previewVideo:function(vid_id){
      var elem = document.getElementById('video-iframe');
      var tmpSRC = 'https://www.youtube.com/embed/'+vid_id+'?controls=0&showinfo=0&rel=0&autoplay=1&loop=1';
      elem.setAttribute('src',tmpSRC);

    },
    search:function(){
      var elem = document.getElementById('search-input');
      app.search_results = [];
      if(elem.value != ''){
        var query = elem.value;
        app.searchGoogle( encodeURIComponent(query) );
      }
    },
    searchGoogle:function(query){
      fetch('/search?q='+query)
      .then(
        function(response) {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' +
              response.status);
            return;
          }


          response.json().then(function(data) {
            console.log('google search results',data);
            app.search_results = data.results;
          });
        }
      )
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
      });


    },
    checkYAML:function(){
      fetch('/get_yaml')
      .then(
        function(response) {
          if (response.status !== 200) {
            console.log('Looks like there was a problem. Status Code: ' +
              response.status);
            return;
          }


          response.json().then(function(data) {
            
            let entries = Object.values(data);
            app.download_list = entries;
          });
        }
      )
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
      });


    },

  }//end methods

});
