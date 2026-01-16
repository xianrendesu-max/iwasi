let hls = null

function play(url){
  const video = document.getElementById("player")

  if(hls){
    hls.destroy()
    hls = null
  }

  if(Hls.isSupported()){
    hls = new Hls()
    hls.loadSource(url)
    hls.attachMedia(video)
  }else{
    video.src = url
  }
}

function loadComments(id){
 fetch(`/api/comments/${id}`)
 .then(r => r.json())
 .then(d => {
   const c = document.getElementById("comments")
   c.innerHTML = ""

   if(!d.comments){
     c.innerText = "コメントなし"
     return
   }

   d.comments.forEach(x => {
     c.innerHTML += `
      <div class="comment">
        <strong>${x.author}</strong><br>
        ${x.content}
      </div>`
   })
 })
}
