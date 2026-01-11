function initPlayer(src){
 const v=document.getElementById("video");
 if(src.endsWith(".m3u8") && Hls.isSupported()){
  const h=new Hls(); h.loadSource(src); h.attachMedia(v);
 }else v.src=src;
}

document.getElementById("quality")?.addEventListener("change",e=>{
 initPlayer(e.target.value);
});

function addFav(){
 const id=location.pathname.split("/").pop();
 let f=JSON.parse(localStorage.getItem("fav")||"[]");
 if(!f.includes(id)) f.push(id);
 localStorage.setItem("fav",JSON.stringify(f));
}

function saveHistory(id){
 let h=JSON.parse(localStorage.getItem("hist")||"[]");
 h.unshift(id); h=[...new Set(h)].slice(0,50);
 localStorage.setItem("hist",JSON.stringify(h));
}
