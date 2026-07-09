/* 教师考编面试系统 - 主JS */
function $(sel){return document.querySelector(sel)}
function $$(sel){return document.querySelectorAll(sel)}
document.addEventListener('DOMContentLoaded',function(){
    console.log('合肥经开区初中音乐考编面试系统已加载');
});
document.addEventListener('click',function(e){
    if(e.target&&e.target.classList.contains('modal')){
        e.target.style.display='none';
    }
});
document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){
        document.querySelectorAll('.modal').forEach(function(m){m.style.display='none'});
    }
});
